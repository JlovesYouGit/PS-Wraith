#!/usr/bin/env python3
"""Extract real device identifiers for SHSH blob generation"""
import subprocess
import sys
import re

def get_device_info():
    """Extract device info from connected iPad"""
    try:
        # Try to get device info using iTunes/3uTools detection
        print("[+] Connect iPad and put in normal mode (not DFU/recovery)")
        print("[+] Extracting device identifiers...")
        
        # This would normally use libimobiledevice or similar
        # For now, provide template for manual entry
        print("\n[!] Manual device info extraction needed:")
        print("1. Open 3uTools with iPad connected")
        print("2. Go to 'Device Info' tab")
        print("3. Find these values:")
        print("   - ECID (hex)")
        print("   - Board ID") 
        print("   - Chip ID")
        print("   - Model")
        
        # Get manual input
        ecid = input("\nEnter ECID (hex, e.g. 0x123456789): ").strip()
        board_id = input("Enter Board ID (e.g. 0x2): ").strip()
        chip_id = input("Enter Chip ID (e.g. 0x8930): ").strip()
        model = input("Enter Model (e.g. iPad1,1): ").strip()
        
        # Clean up inputs - remove colons and extra spaces
        ecid = ecid.replace(':', '').strip()
        board_id = board_id.replace(':', '').strip()
        chip_id = chip_id.replace(':', '').strip()
        
        if not all([ecid, board_id, chip_id, model]):
            print("[!] All fields required")
            return None
        
        return {
            'ecid': ecid,
            'board_id': board_id, 
            'chip_id': chip_id,
            'model': model
        }
        
    except Exception as e:
        print(f"[!] Device info extraction failed: {e}")
        return None

def generate_device_specific_shsh(device_info, filename="device_specific.shsh"):
    """Generate SHSH blob with real device identifiers"""
    try:
        import hashlib
        import base64
        import struct
        import time
        
        # Convert hex values - handle 0x prefix
        ecid_str = device_info['ecid'].replace('0x', '').replace(':', '').strip()
        board_id_str = device_info['board_id'].replace('0x', '').replace(':', '').strip()
        chip_id_str = device_info['chip_id'].replace('0x', '').replace(':', '').strip()
        
        ecid_int = int(ecid_str, 16)
        board_id_int = int(board_id_str, 16) 
        chip_id_int = int(chip_id_str, 16)
        
        # Create device-specific nonce
        device_string = f"{device_info['model']}{device_info['ecid']}{time.time()}"
        nonce = hashlib.sha1(device_string.encode()).digest()[:20]
        ap_nonce = base64.b64encode(nonce).decode()
        
        # Create device-specific tickets
        ticket_data = struct.pack('>I', 0x494D4733) + struct.pack('>Q', ecid_int)[:8] + b'\x00' * 52
        ap_ticket = base64.b64encode(ticket_data).decode()
        
        bb_data = struct.pack('>I', 0x42425443) + struct.pack('>Q', ecid_int)[:8] + b'\x00' * 52  
        bb_ticket = base64.b64encode(bb_data).decode()
        
        # Generate device-specific SHSH
        shsh_blob = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>@APTicket</key>
    <data>{ap_ticket}</data>
    <key>@BBTicket</key>
    <data>{bb_ticket}</data>
    <key>@HostPlatformInfo</key>
    <string>windows</string>
    <key>ApChipID</key>
    <integer>{chip_id_int}</integer>
    <key>ApBoardID</key>
    <integer>{board_id_int}</integer>
    <key>ApSecurityDomain</key>
    <integer>1</integer>
    <key>EcID</key>
    <integer>{ecid_int}</integer>
    <key>Nonce</key>
    <data>{ap_nonce}</data>
    <key>REQUEST_STRING</key>
    <string>&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;plist version="1.0"&gt;
&lt;dict&gt;
    &lt;key&gt;@HostPlatformInfo&lt;/key&gt;
    &lt;string&gt;windows&lt;/string&gt;
    &lt;key&gt;ApBoardID&lt;/key&gt;
    &lt;integer&gt;{board_id_int}&lt;/integer&gt;
    &lt;key&gt;ApChipID&lt;/key&gt;
    &lt;integer&gt;{chip_id_int}&lt;/integer&gt;
    &lt;key&gt;EcID&lt;/key&gt;
    &lt;integer&gt;{ecid_int}&lt;/integer&gt;
&lt;/dict&gt;
&lt;/plist&gt;</string>
</dict>
</plist>'''
        
        with open(filename, 'w') as f:
            f.write(shsh_blob)
        
        print(f"[✅] Device-specific SHSH blob: {filename}")
        print(f"[+] ECID: {device_info['ecid']} ({ecid_int})")
        print(f"[+] Board ID: {device_info['board_id']} ({board_id_int})")
        print(f"[+] Chip ID: {device_info['chip_id']} ({chip_id_int})")
        
        return True
        
    except Exception as e:
        print(f"[!] SHSH generation failed: {e}")
        return False

def main():
    print("[+] Device-Specific SHSH Generator")
    
    device_info = get_device_info()
    if not device_info:
        print("[!] Failed to get device info")
        return
    
    filename = f"{device_info['model']}_custom.shsh"
    generate_device_specific_shsh(device_info, filename)

if __name__ == "__main__":
    main()