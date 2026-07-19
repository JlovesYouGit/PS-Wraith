#!/usr/bin/env python3
"""
ALWAYS FLIP BIT - Runtime Auto-Boot Enabler
Automatically flips the auto-boot bit (0x02 → 0x03) whenever iPad is detected.
No questions asked, no confirmations - just flip it!
"""
import time
import sys
import subprocess
import json
import re
from typing import Optional, Dict

def get_ipad_recovery() -> Optional[Dict]:
    """Fast iPad detection in recovery mode."""
    try:
        result = subprocess.run([
            sys.executable, "src/usb_scanner.py", "--apple-scan", "--format", "json"
        ], capture_output=True, text=True, timeout=3)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            for device in data.get("devices", []):
                if (device.get("vendor_id") == "0x05AC" and 
                    device.get("product_id") == "0x1281"):
                    
                    instance_id = device.get("instance_id", "")
                    if "IBFL:" in instance_id and "ECID:" in instance_id:
                        ecid_match = re.search(r'ECID:([0-9A-F]+)', instance_id)
                        flags_match = re.search(r'IBFL:([0-9A-F]+)', instance_id)
                        
                        if ecid_match and flags_match:
                            return {
                                "ecid": ecid_match.group(1),
                                "flags": int(flags_match.group(1), 16),
                                "flags_hex": flags_match.group(1)
                            }
        return None
    except:
        return None

def flip_bit_now(ipad_data: Dict) -> bool:
    """FLIP THE BIT NOW - No delays, no questions!"""
    try:
        import irecovery
        
        # Connect immediately
        device = irecovery.IRecovery()
        if not device:
            return False
        
        current_flags = ipad_data["flags"]
        
        # Check if bit 0 is already set
        if current_flags & 0x01:
            print(f"✅ Bit already flipped! (0x{current_flags:02X})")
            return True
        
        # FLIP IT NOW!
        print(f"🔧 FLIPPING BIT: 0x{current_flags:02X} → 0x{current_flags | 0x01:02X}")
        
        # Send commands rapidly
        device.send_command(b"setenv auto-boot true\n")
        device.send_command(b"saveenv\n")
        device.send_command(b"reboot\n")
        
        print("✅ BIT FLIPPED! iPad will now auto-boot!")
        return True
        
    except Exception as e:
        print(f"❌ Flip failed: {e}")
        return False

def runtime_flipper():
    """Runtime bit flipper - always watching, always flipping."""
    print("🚀 ALWAYS FLIP BIT - Runtime Mode")
    print("=" * 40)
    print("Watching for iPad... Will flip bit 0 immediately!")
    print("Press Ctrl+C to stop\n")
    
    processed_ecids = set()
    
    try:
        while True:
            ipad = get_ipad_recovery()
            
            if ipad:
                ecid = ipad["ecid"]
                
                # Process each unique device once per session
                if ecid not in processed_ecids:
                    print(f"📱 iPad ECID {ecid} detected!")
                    print(f"   Current flags: 0x{ipad['flags']:02X}")
                    
                    if flip_bit_now(ipad):
                        processed_ecids.add(ecid)
                        print(f"   ✅ ECID {ecid} processed - bit flipped!\n")
                    else:
                        print(f"   ❌ Failed to flip bit for ECID {ecid}\n")
            
            time.sleep(0.5)  # Check twice per second
            
    except KeyboardInterrupt:
        print("\n🛑 Runtime flipper stopped")

def single_flip():
    """Single-shot bit flip."""
    print("🔧 Single Bit Flip Mode")
    print("=" * 25)
    
    ipad = get_ipad_recovery()
    
    if not ipad:
        print("❌ No iPad in recovery mode found")
        return False
    
    print(f"📱 iPad ECID {ipad['ecid']} found")
    print(f"   Current flags: 0x{ipad['flags']:02X}")
    
    return flip_bit_now(ipad)

def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--runtime":
        runtime_flipper()
    else:
        if single_flip():
            print("✅ Success!")
            return 0
        else:
            print("❌ Failed!")
            return 1

if __name__ == "__main__":
    sys.exit(main())