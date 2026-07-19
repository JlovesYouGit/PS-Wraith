#!/usr/bin/env python3
"""
Runtime Boot Manager - Always flip the auto-boot bit
Automatically detects and fixes iPad boot issues in real-time.
"""
import time
import threading
import sys
from typing import Optional
import subprocess
import json

class iPadBootManager:
    """
    Real-time iPad boot management system.
    Automatically flips auto-boot bit whenever iPad is detected.
    """
    
    def __init__(self):
        self.running = False
        self.monitor_thread = None
        self.last_processed_ecid = None
        
    def detect_ipad_recovery(self) -> Optional[dict]:
        """Quick iPad detection in recovery mode."""
        try:
            result = subprocess.run([
                sys.executable, "src/usb_scanner.py", "--apple-scan", "--format", "json"
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                for device in data.get("devices", []):
                    if (device.get("vendor_id") == "0x05AC" and 
                        device.get("product_id") == "0x1281"):
                        
                        instance_id = device.get("instance_id", "")
                        if "IBFL:" in instance_id and "ECID:" in instance_id:
                            import re
                            
                            ecid_match = re.search(r'ECID:([0-9A-F]+)', instance_id)
                            flags_match = re.search(r'IBFL:([0-9A-F]+)', instance_id)
                            
                            if ecid_match and flags_match:
                                return {
                                    "ecid": ecid_match.group(1),
                                    "iboot_flags": flags_match.group(1),
                                    "device_name": device.get("name", "iPad")
                                }
            return None
        except:
            return None
    
    def flip_bit_immediately(self, ipad_info: dict) -> bool:
        """Immediately flip the auto-boot bit."""
        try:
            import irecovery
            
            # Quick connection attempt
            device = irecovery.IRecovery()
            if not device:
                return False
            
            current_flags = int(ipad_info.get("iboot_flags", "02"), 16)
            
            # Only flip if auto-boot is disabled
            if not (current_flags & 0x01):
                print(f"🔧 Flipping auto-boot bit for ECID {ipad_info['ecid']}...")
                
                # Send commands rapidly
                device.send_command(b"setenv auto-boot true\n")
                time.sleep(0.1)
                device.send_command(b"saveenv\n")
                time.sleep(0.1)
                device.send_command(b"reboot\n")
                
                print(f"✅ Auto-boot enabled! (0x{current_flags:02X} → 0x{current_flags | 0x01:02X})")
                return True
            else:
                print(f"✅ Auto-boot already enabled for ECID {ipad_info['ecid']}")
                return True
                
        except Exception as e:
            print(f"❌ Error flipping bit: {e}")
            return False
    
    def monitor_loop(self):
        """Continuous monitoring loop."""
        print("🔍 Runtime Boot Manager Active")
        print("Monitoring for iPad devices...")
        
        while self.running:
            try:
                ipad_info = self.detect_ipad_recovery()
                
                if ipad_info:
                    current_ecid = ipad_info["ecid"]
                    
                    # Process each new device detection
                    if current_ecid != self.last_processed_ecid:
                        print(f"\n📱 iPad detected: {ipad_info['device_name']}")
                        print(f"   ECID: {current_ecid}")
                        
                        # Immediately attempt to flip the bit
                        if self.flip_bit_immediately(ipad_info):
                            self.last_processed_ecid = current_ecid
                        
                        print("   Continuing to monitor...\n")
                
                time.sleep(1)  # Check every second
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Monitor error: {e}")
                time.sleep(2)
    
    def start_monitoring(self):
        """Start the monitoring thread."""
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self.monitor_thread.start()
            print("🚀 Runtime monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring thread."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        print("🛑 Runtime monitoring stopped")

def main():
    """Main runtime boot manager."""
    print("🔧 iPad Runtime Boot Manager")
    print("=" * 40)
    print("This tool automatically flips the auto-boot bit whenever an iPad is detected.")
    print("Press Ctrl+C to stop\n")
    
    manager = iPadBootManager()
    
    try:
        manager.start_monitoring()
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        manager.stop_monitoring()
        print("✅ Runtime Boot Manager stopped")

if __name__ == "__main__":
    main()