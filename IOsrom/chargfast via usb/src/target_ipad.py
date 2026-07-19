#!/usr/bin/env python
"""
Simple iPad targeting script for charging management.
"""
import json
import sys
import subprocess
from typing import Optional, Dict, Any

def get_connected_ipad() -> Optional[Dict[str, Any]]:
    """
    Get the connected iPad device information.
    Returns the primary iPad device info or None if not found.
    """
    try:
        # Run the iPad finder
        result = subprocess.run([
            sys.executable, "src/ipad_finder.py"
        ], capture_output=True, text=True)
        
        # Also get the raw Apple scan data
        scan_result = subprocess.run([
            sys.executable, "src/usb_scanner.py", "--apple-scan", "--format", "json"
        ], capture_output=True, text=True)
        
        if scan_result.returncode == 0:
            data = json.loads(scan_result.stdout)
            apple_devices = [d for d in data.get("devices", []) if d.get("vendor_id") == "0x05AC"]
            
            # Find the most descriptive iPad device
            ipad_device = None
            for device in apple_devices:
                if device.get("product_id") in ["0x1281", "0x1227"]:  # iPad PIDs
                    # Prefer the one with ECID info (more complete)
                    if "ECID:" in device.get("instance_id", ""):
                        ipad_device = device
                        break
                    elif not ipad_device:
                        ipad_device = device
            
            if ipad_device:
                # Extract device info
                instance_id = ipad_device.get("instance_id", "")
                device_info = {
                    "found": True,
                    "vendor_id": ipad_device.get("vendor_id"),
                    "product_id": ipad_device.get("product_id"),
                    "name": ipad_device.get("name"),
                    "instance_id": instance_id,
                    "device_class": ipad_device.get("device_class"),
                    "manufacturer": ipad_device.get("manufacturer"),
                    "status": ipad_device.get("status")
                }
                
                # Extract ECID if present
                if "ECID:" in instance_id:
                    import re
                    ecid_match = re.search(r'ECID:([0-9A-F]+)', instance_id)
                    if ecid_match:
                        device_info["ecid"] = ecid_match.group(1)
                
                return device_info
        
        return None
        
    except Exception as e:
        print(f"Error finding iPad: {e}", file=sys.stderr)
        return None

def main():
    """Main function to target the iPad."""
    print("🎯 iPad Targeting Script")
    print("=" * 30)
    
    ipad = get_connected_ipad()
    
    if not ipad:
        print("❌ No iPad found!")
        print("\nMake sure:")
        print("- iPad is connected via USB")
        print("- iPad is recognized by Windows")
        print("- Try different USB ports/cables")
        return 1
    
    print("✅ iPad Found!")
    print(f"📱 Device: {ipad['name']}")
    print(f"🔌 Vendor ID: {ipad['vendor_id']}")
    print(f"🔌 Product ID: {ipad['product_id']}")
    if ipad.get('ecid'):
        print(f"🆔 ECID: {ipad['ecid']}")
    print(f"📋 Target Instance ID:")
    print(f"   {ipad['instance_id']}")
    
    print("\n🎯 TARGETING INFORMATION:")
    print("=" * 40)
    print("Use this information to target your iPad:")
    print(f"Vendor ID: {ipad['vendor_id']}")
    print(f"Product ID: {ipad['product_id']}")
    if ipad.get('ecid'):
        print(f"Unique ECID: {ipad['ecid']}")
    print(f"Full Instance ID: {ipad['instance_id']}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())