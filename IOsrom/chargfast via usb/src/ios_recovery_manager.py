#!/usr/bin/env python
"""
iOS Recovery Manager - Integrates with irecovery for iOS device management.
"""
import json
import sys
import subprocess
import os
import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

class iOSRecoveryManager:
    def __init__(self):
        self.irecovery_path = self._find_irecovery()
        
    def _find_irecovery(self) -> Optional[str]:
        """Find irecovery executable in current directory or PATH."""
        # Check current directory first
        current_dir = Path.cwd()
        irecovery_exe = current_dir / "irecovery.exe"
        if irecovery_exe.exists():
            return str(irecovery_exe)
        
        # Check PATH
        try:
            result = subprocess.run(["where", "irecovery"], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except:
            pass
        
        return None
    
    def is_available(self) -> bool:
        """Check if irecovery is available."""
        return self.irecovery_path is not None
    
    def get_device_info(self) -> Optional[Dict[str, Any]]:
        """Get iOS device information using irecovery."""
        if not self.is_available():
            return None
        
        try:
            # Try to get device info
            result = subprocess.run([
                self.irecovery_path, "-q"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # Parse irecovery output
                info = {}
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if ':' in line:
                        key, value = line.split(':', 1)
                        info[key.strip().lower().replace(' ', '_')] = value.strip()
                
                return {
                    "connected": True,
                    "tool": "irecovery",
                    "device_info": info
                }
            else:
                return {
                    "connected": False,
                    "tool": "irecovery",
                    "error": result.stderr.strip() if result.stderr else "Device not found"
                }
        
        except subprocess.TimeoutExpired:
            return {
                "connected": False,
                "tool": "irecovery", 
                "error": "Connection timeout"
            }
        except Exception as e:
            return {
                "connected": False,
                "tool": "irecovery",
                "error": str(e)
            }
    
    def set_auto_boot(self, enabled: bool = True) -> Dict[str, Any]:
        """Set auto-boot flag on iOS device."""
        if not self.is_available():
            return {"success": False, "error": "irecovery not available"}
        
        try:
            value = "true" if enabled else "false"
            
            # Execute the commands
            commands = [
                f"setenv auto-boot {value}",
                "saveenv",
                "reboot"
            ]
            
            for cmd in commands:
                result = subprocess.run([
                    self.irecovery_path, "-c", cmd
                ], capture_output=True, text=True, timeout=15)
                
                if result.returncode != 0:
                    return {
                        "success": False,
                        "error": f"Command '{cmd}' failed: {result.stderr}",
                        "command": cmd
                    }
            
            return {
                "success": True,
                "message": f"Auto-boot set to {value} and device rebooted"
            }
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def send_command(self, command: str) -> Dict[str, Any]:
        """Send a custom command to the iOS device."""
        if not self.is_available():
            return {"success": False, "error": "irecovery not available"}
        
        try:
            result = subprocess.run([
                self.irecovery_path, "-c", command
            ], capture_output=True, text=True, timeout=15)
            
            return {
                "success": result.returncode == 0,
                "command": command,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

def scan_ios_devices() -> List[Dict[str, Any]]:
    """Scan for iOS devices using multiple methods."""
    devices = []
    
    # Method 1: Use our existing USB scanner for Apple devices
    try:
        result = subprocess.run([
            sys.executable, "src/usb_scanner.py", "--apple-scan", "--format", "json"
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            apple_devices = [d for d in data.get("devices", []) if d.get("vendor_id") == "0x05AC"]
            
            for device in apple_devices:
                devices.append({
                    "method": "USB Scanner",
                    "device": device,
                    "is_ios": True
                })
    except:
        pass
    
    # Method 2: Use irecovery to get recovery mode device info
    recovery_manager = iOSRecoveryManager()
    if recovery_manager.is_available():
        ios_info = recovery_manager.get_device_info()
        if ios_info and ios_info.get("connected"):
            devices.append({
                "method": "irecovery",
                "device": ios_info,
                "is_ios": True
            })
    
    return devices

def main():
    """Main function for iOS recovery management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="iOS Recovery Manager")
    parser.add_argument("--scan", action="store_true", help="Scan for iOS devices")
    parser.add_argument("--info", action="store_true", help="Get device info via irecovery")
    parser.add_argument("--auto-boot", choices=["enable", "disable"], help="Set auto-boot flag")
    parser.add_argument("--command", "-c", help="Send custom command to device")
    parser.add_argument("--format", choices=["json", "text"], default="text", help="Output format")
    
    args = parser.parse_args()
    
    recovery_manager = iOSRecoveryManager()
    
    if args.scan:
        print("🔍 Scanning for iOS devices...")
        devices = scan_ios_devices()
        
        if args.format == "json":
            print(json.dumps({
                "timestamp": datetime.datetime.now().isoformat(),
                "device_count": len(devices),
                "devices": devices
            }, indent=2))
        else:
            print(f"Found {len(devices)} iOS device(s):")
            for i, device_info in enumerate(devices, 1):
                print(f"\nDevice {i} ({device_info['method']}):")
                device = device_info['device']
                if device_info['method'] == 'USB Scanner':
                    print(f"  Name: {device.get('name', 'Unknown')}")
                    print(f"  Vendor ID: {device.get('vendor_id', 'Unknown')}")
                    print(f"  Product ID: {device.get('product_id', 'Unknown')}")
                    print(f"  Status: {device.get('status', 'Unknown')}")
                elif device_info['method'] == 'irecovery':
                    if device.get('connected'):
                        info = device.get('device_info', {})
                        for key, value in info.items():
                            print(f"  {key.replace('_', ' ').title()}: {value}")
                    else:
                        print(f"  Error: {device.get('error', 'Unknown error')}")
    
    elif args.info:
        if not recovery_manager.is_available():
            print("❌ irecovery not found. Make sure irecovery.exe is in the current directory.")
            return 1
        
        print("📱 Getting iOS device info...")
        info = recovery_manager.get_device_info()
        
        if args.format == "json":
            print(json.dumps(info, indent=2))
        else:
            if info and info.get("connected"):
                print("✅ iOS device connected!")
                device_info = info.get("device_info", {})
                for key, value in device_info.items():
                    print(f"  {key.replace('_', ' ').title()}: {value}")
            else:
                print(f"❌ No iOS device found: {info.get('error', 'Unknown error') if info else 'No response'}")
    
    elif args.auto_boot:
        if not recovery_manager.is_available():
            print("❌ irecovery not found. Make sure irecovery.exe is in the current directory.")
            return 1
        
        enabled = args.auto_boot == "enable"
        print(f"🔧 {'Enabling' if enabled else 'Disabling'} auto-boot...")
        
        result = recovery_manager.set_auto_boot(enabled)
        
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            if result.get("success"):
                print(f"✅ {result.get('message')}")
            else:
                print(f"❌ Failed: {result.get('error')}")
                return 1
    
    elif args.command:
        if not recovery_manager.is_available():
            print("❌ irecovery not found. Make sure irecovery.exe is in the current directory.")
            return 1
        
        print(f"📤 Sending command: {args.command}")
        result = recovery_manager.send_command(args.command)
        
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            if result.get("success"):
                print("✅ Command executed successfully")
                if result.get("output"):
                    print(f"Output: {result['output']}")
            else:
                print(f"❌ Command failed: {result.get('error')}")
                return 1
    
    else:
        parser.print_help()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
