#!/usr/bin/env python3
"""
GoldHEN Integration Module
Integrates GoldHEN PS4 Homebrew Enabler payload into wraith system
Handles payload deployment, version management, and device communication
"""

import os
import sys
import json
import time
import hashlib
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

# Paths
GOLDHEN_DIR = Path(__file__).parent / "GoldHEN"
GOLDHEN_BIN = GOLDHEN_DIR / "goldhen.bin"
GOLDHEN_CONFIG = GOLDHEN_DIR / "config.ini"
GOLDHEN_CHEATS = GOLDHEN_DIR / "cheats"


@dataclass
class GoldHENPayload:
    """Represents a GoldHEN payload"""
    version: str
    firmware_support: List[str]
    features: List[str]
    binary_path: Path
    sha256: str
    size: int
    timestamp: str


@dataclass
class GoldHENConfig:
    """GoldHEN configuration"""
    enabled: bool = True
    ftp_enabled: bool = True
    ftp_port: int = 21
    binloader_enabled: bool = True
    binloader_port: int = 9090
    klog_enabled: bool = True
    klog_port: int = 3232
    cheat_menu_enabled: bool = True
    plugins_enabled: bool = True
    external_hdd_enabled: bool = True
    debug_trophies: bool = True
    screenshot_enabled: bool = True
    rest_mode_supported: bool = True
    remote_pkg_install: bool = True
    vr_support: bool = True
    firmware_update_block: bool = True
    uart_enabled: bool = False
    sys_dynlib_dlsym_patch: bool = True


class GoldHENIntegration:
    """
    GoldHEN integration for wraith system
    Manages payload deployment and configuration
    """
    
    def __init__(self, work_dir: Path, flash_mode: bool = False):
        self.work_dir = work_dir
        self.flash_mode = flash_mode
        self.goldhen_dir = GOLDHEN_DIR
        self.payload: Optional[GoldHENPayload] = None
        self.config = GoldHENConfig()
        self.deployed = False
        self.device_connected = False
        self._load_payload()
        self._load_config()
    
    def _load_payload(self) -> None:
        """Load GoldHEN payload information"""
        if not GOLDHEN_BIN.exists():
            print(f"[GoldHEN] Payload not found: {GOLDHEN_BIN}")
            return
        
        # Calculate hash and size
        sha256 = hashlib.sha256(GOLDHEN_BIN.read_bytes()).hexdigest()[:16]
        size = GOLDHEN_BIN.stat().st_size
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%S%z", time.gmtime(GOLDHEN_BIN.stat().st_mtime))
        
        # Parse version from directory name or binary
        version = "2.4b17.3"
        if "GoldHEN-" in str(self.goldhen_dir):
            version = str(self.goldhen_dir.name).replace("GoldHEN-", "")
        
        self.payload = GoldHENPayload(
            version=version,
            firmware_support=["5.05", "6.72", "7.02", "7.5x", "8.0x", "9.00", "10.00", "10.01", "11.00", "9.60"],
            features=[
                "Homebrew Enabler",
                "Debug Settings",
                "VR Support",
                "Remote Package Install",
                "Rest Mode Support",
                "External HDD Support",
                "Debug Trophies Support",
                "sys_dynlib_dlsym Patch",
                "UART Enabler",
                "Never Disable Screenshot",
                "Remote Play Enabler",
                "FW Update Block",
                "FTP Server (port 21)",
                "BinLoader Server (port 9090)",
                "Klog Server (port 3232)",
                "CE-30391-6 Error CMOS Fix",
                "Integrated Cheat Menu",
                "Integrated FPS Counter",
                "Plugins support",
                "TitleId label feature",
                "Scanlines overlay",
                "Internal pkg installation support"
            ],
            binary_path=GOLDHEN_BIN,
            sha256=sha256,
            size=size,
            timestamp=timestamp
        )
    
    def _load_config(self) -> None:
        """Load GoldHEN configuration"""
        config_path = self.work_dir / "GoldHEN" / "config.ini"
        if config_path.exists():
            try:
                # Parse INI-like config
                content = config_path.read_text()
                for line in content.splitlines():
                    line = line.strip()
                    if line.startswith("#") or "=" not in line:
                        continue
                    key, _, value = line.partition("=")
                    key = key.strip().lower()
                    value = value.strip().lower()
                    
                    if hasattr(self.config, key):
                        setattr(self.config, key, value in ("1", "true", "yes", "on"))
            except Exception as e:
                print(f"[GoldHEN] Config load error: {e}")
    
    def get_payload_info(self) -> Dict[str, Any]:
        """Get payload information"""
        if not self.payload:
            return {"error": "No payload loaded"}
        
        return {
            "version": self.payload.version,
            "firmware_support": self.payload.firmware_support,
            "features": self.payload.features,
            "sha256": self.payload.sha256,
            "size": self.payload.size,
            "size_mb": round(self.payload.size / (1024 * 1024), 2),
            "timestamp": self.payload.timestamp,
            "binary_path": str(self.payload.binary_path)
        }
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return asdict(self.config)
    
    def update_config(self, **kwargs) -> Dict[str, Any]:
        """Update configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        # Save config
        config_path = self.work_dir / "GoldHEN" / "config.ini"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        lines = ["# GoldHEN Configuration\n", "# Auto-generated by wraith system\n", "\n"]
        for key, value in asdict(self.config).items():
            lines.append(f"{key} = {1 if value else 0}\n")
        
        config_path.write_text("".join(lines))
        
        return self.get_config()
    
    def deploy_payload(self, target_ip: Optional[str] = None, target_port: int = 9090) -> Dict[str, Any]:
        """
        Deploy GoldHEN payload to PS4 device
        
        Args:
            target_ip: Target device IP (from latching system)
            target_port: Target port for payload delivery
        """
        if not self.payload:
            return {"success": False, "error": "No payload loaded"}
        
        if not GOLDHEN_BIN.exists():
            return {"success": False, "error": f"Payload not found: {GOLDHEN_BIN}"}
        
        print(f"[GoldHEN] Deploying payload v{self.payload.version}...")
        print(f"[GoldHEN] Target: {target_ip or 'auto-detect'}:{target_port}")
        print(f"[GoldHEN] Size: {self.payload.size} bytes ({self.payload.size_mb} MB)")
        
        result = {
            "success": False,
            "version": self.payload.version,
            "target_ip": target_ip,
            "target_port": target_port,
            "method": None,
            "error": None
        }
        
        # Method 1: Direct TCP socket deployment
        if target_ip:
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((target_ip, target_port))
                
                # Send payload
                payload_data = GOLDHEN_BIN.read_bytes()
                sock.sendall(payload_data)
                
                sock.close()
                result["success"] = True
                result["method"] = "tcp_direct"
                print(f"[GoldHEN] Deployed via TCP to {target_ip}:{target_port}")
                return result
            except Exception as e:
                print(f"[GoldHEN] TCP deployment failed: {e}")
                result["error"] = str(e)
        
        # Method 2: Via irecovery (USB)
        try:
            deploy_result = subprocess.run(
                ["irecovery", "-f", str(GOLDHEN_BIN)],
                capture_output=True, text=True, timeout=30
            )
            if deploy_result.returncode == 0:
                result["success"] = True
                result["method"] = "irecovery"
                print("[GoldHEN] Deployed via irecovery")
                return result
        except Exception as e:
            print(f"[GoldHEN] iRecovery deployment failed: {e}")
            if not result["error"]:
                result["error"] = str(e)
        
        # Method 3: Save to transfer directory
        try:
            transfer_dir = self.work_dir / "library_mirror" / "payloads"
            transfer_dir.mkdir(parents=True, exist_ok=True)
            dest = transfer_dir / "goldhen.bin"
            shutil.copy2(GOLDHEN_BIN, dest)
            result["success"] = True
            result["method"] = "file_transfer"
            result["transfer_path"] = str(dest)
            print(f"[GoldHEN] Payload saved to: {dest}")
            return result
        except Exception as e:
            print(f"[GoldHEN] File transfer failed: {e}")
            result["error"] = str(e)
        
        return result
    
    def setup_cheats_directory(self) -> Dict[str, Any]:
        """Setup cheats directory structure"""
        cheats_dir = self.work_dir / "GoldHEN" / "cheats"
        cheats_dir.mkdir(parents=True, exist_ok=True)
        
        subdirs = {
            "json": cheats_dir / "json",
            "shn": cheats_dir / "shn",
            "mc4": cheats_dir / "mc4"
        }
        
        for name, dir_path in subdirs.items():
            dir_path.mkdir(exist_ok=True)
        
        return {
            "cheats_dir": str(cheats_dir),
            "subdirs": {k: str(v) for k, v in subdirs.items()},
            "max_cheat_files": 8
        }
    
    def generate_wraith_config(self) -> Dict[str, Any]:
        """Generate wraith configuration for GoldHEN"""
        return {
            "goldhen": {
                "active": True,
                "version": self.payload.version if self.payload else "unknown",
                "payload_path": str(GOLDHEN_BIN),
                "config": self.get_config(),
                "deployment": {
                    "method": "tcp_direct",
                    "port": 9090,
                    "fallback_ports": [8080, 80, 443, 2121, 3232]
                },
                "features": {
                    "ftp": {"enabled": self.config.ftp_enabled, "port": self.config.ftp_port},
                    "binloader": {"enabled": self.config.binloader_enabled, "port": self.config.binloader_port},
                    "klog": {"enabled": self.config.klog_enabled, "port": self.config.klog_port},
                    "cheat_menu": {"enabled": self.config.cheat_menu_enabled},
                    "plugins": {"enabled": self.config.plugins_enabled},
                    "external_hdd": {"enabled": self.config.external_hdd_enabled},
                    "debug_trophies": {"enabled": self.config.debug_trophies},
                    "screenshot": {"enabled": self.config.screenshot_enabled},
                    "rest_mode": {"enabled": self.config.rest_mode_supported},
                    "remote_pkg": {"enabled": self.config.remote_pkg_install},
                    "vr": {"enabled": self.config.vr_support},
                    "fw_block": {"enabled": self.config.firmware_update_block},
                    "uart": {"enabled": self.config.uart_enabled},
                    "dlsym_patch": {"enabled": self.config.sys_dynlib_dlsym_patch}
                },
                "cheats": {
                    "directory": str(self.work_dir / "GoldHEN" / "cheats"),
                    "max_files": 8,
                    "formats": ["json", "shn", "mc4"]
                }
            }
        }
    
    def integrate_with_wraith(self, wraith_config: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate GoldHEN with wraith configuration"""
        goldhen_config = self.generate_wraith_config()
        
        # Merge with wraith config
        if "goldhen" not in wraith_config:
            wraith_config["goldhen"] = goldhen_config["goldhen"]
        else:
            wraith_config["goldhen"].update(goldhen_config["goldhen"])
        
        # Add GoldHEN to scripts
        if "scripts" not in wraith_config:
            wraith_config["scripts"] = {}
        
        wraith_config["scripts"].update({
            "goldhen-deploy": "node CONTROL_CENTER.js goldhen-deploy",
            "goldhen-config": "node CONTROL_CENTER.js goldhen-config",
            "goldhen-cheats": "node CONTROL_CENTER.js goldhen-cheats",
            "goldhen-status": "node CONTROL_CENTER.js goldhen-status"
        })
        
        # Add to files list
        if "files" not in wraith_config:
            wraith_config["files"] = []
        
        goldhen_files = [
            "GoldHEN/goldhen.bin",
            "GoldHEN/config.ini",
            "GoldHEN/cheats/json/",
            "GoldHEN/cheats/shn/",
            "GoldHEN/cheats/mc4/"
        ]
        
        for f in goldhen_files:
            if f not in wraith_config["files"]:
                wraith_config["files"].append(f)
        
        return wraith_config
    
    def get_status(self) -> Dict[str, Any]:
        """Get GoldHEN integration status"""
        return {
            "payload_loaded": self.payload is not None,
            "payload_info": self.get_payload_info() if self.payload else None,
            "config": self.get_config(),
            "deployed": self.deployed,
            "device_connected": self.device_connected,
            "goldhen_dir": str(self.goldhen_dir),
            "payload_exists": GOLDHEN_BIN.exists(),
            "cheats_dir": str(self.work_dir / "GoldHEN" / "cheats")
        }


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='GoldHEN Integration')
    parser.add_argument('work_dir', help='Working directory')
    parser.add_argument('--deploy', action='store_true', help='Deploy payload')
    parser.add_argument('--config', action='store_true', help='Show configuration')
    parser.add_argument('--cheats', action='store_true', help='Setup cheats directory')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--ip', help='Target IP for deployment')
    parser.add_argument('--port', type=int, default=9090, help='Target port')
    
    args = parser.parse_args()
    
    integration = GoldHENIntegration(Path(args.work_dir))
    
    if args.status:
        status = integration.get_status()
        print(json.dumps(status, indent=2))
        return 0
    
    if args.config:
        config = integration.get_config()
        print(json.dumps(config, indent=2))
        return 0
    
    if args.cheats:
        result = integration.setup_cheats_directory()
        print(json.dumps(result, indent=2))
        return 0
    
    if args.deploy:
        result = integration.deploy_payload(target_ip=args.ip, target_port=args.port)
        print(json.dumps(result, indent=2))
        return 0 if result.get("success") else 1
    
    # Default: show payload info
    info = integration.get_payload_info()
    print(json.dumps(info, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
