#!/usr/bin/env python
"""
iPad-specific USB device finder and analyzer.
"""
import json
import sys
import subprocess
from typing import List, Dict, Any

def find_ipad_devices() -> List[Dict[str, Any]]:
    """
    Find and analyze iPad devices specifically, deduplicating multiple interfaces.
    """
    try:
        # Run the enhanced Apple scan
        result = subprocess.run([
            sys.executable, "src/usb_scanner.py", "--apple-scan", "--format", "json"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            devices = data.get("devices", [])
            
            # Filter for Apple devices (VID 0x05AC)
            apple_devices = [d for d in devices if d.get("vendor_id") == "0x05AC"]
            
            # Deduplicate devices by extracting unique physical devices
            unique_devices = deduplicate_apple_devices(apple_devices)
            
            # Analyze each unique Apple device
            ipad_devices = []
            for device in unique_devices:
                device_analysis = analyze_apple_device(device)
                if device_analysis:
                    ipad_devices.append(device_analysis)
            
            return ipad_devices
        
        return []
        
    except Exception as e:
        print(f"Error finding iPad devices: {e}", file=sys.stderr)
        return []

def deduplicate_apple_devices(devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deduplicate Apple devices that appear multiple times due to multiple interfaces.
    """
    unique_devices = {}
    
    for device in devices:
        instance_id = device.get("instance_id", "")
        
        # Extract the base device identifier (before &MI_ interface specifier)
        base_id = instance_id
        if "&MI_" in instance_id:
            base_id = instance_id.split("&MI_")[0]
        
        # Extract ECID if present (unique device identifier)
        ecid = None
        if "ECID:" in instance_id:
            import re
            ecid_match = re.search(r'ECID:([0-9A-F]+)', instance_id)
            if ecid_match:
                ecid = ecid_match.group(1)
                base_id = f"ECID_{ecid}"
        
        # Use the most descriptive device name available
        if base_id not in unique_devices or len(device.get("name", "")) > len(unique_devices[base_id].get("name", "")):
            # Prefer devices with more descriptive names or recovery mode info
            if "recovery" in device.get("name", "").lower() or "iboot" in device.get("name", "").lower():
                unique_devices[base_id] = device
            elif base_id not in unique_devices:
                unique_devices[base_id] = device
    
    return list(unique_devices.values())

def analyze_apple_device(device: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze an Apple device to determine if it's an iPad and its state.
    """
    vendor_id = device.get("vendor_id", "")
    product_id = device.get("product_id", "")
    name = device.get("name", "").lower()
    instance_id = device.get("instance_id", "")
    
    # Apple device analysis
    device_info = {
        "device_type": "Unknown Apple Device",
        "state": "Unknown",
        "is_ipad": False,
        "original_device": device
    }
    
    # Product ID analysis for Apple devices
    pid_analysis = {
        "0x1227": {"type": "iPad", "state": "Recovery Mode (iBoot)", "is_ipad": True},
        "0x1281": {"type": "iPad", "state": "Recovery/DFU Mode", "is_ipad": True},
        "0x12A8": {"type": "iPad", "state": "Normal Mode", "is_ipad": True},
        "0x12AB": {"type": "iPad", "state": "Normal Mode", "is_ipad": True},
        "0x129A": {"type": "iPad", "state": "Normal Mode", "is_ipad": True},
        "0x1290": {"type": "iPhone", "state": "Normal Mode", "is_ipad": False},
        "0x1291": {"type": "iPhone", "state": "Recovery Mode", "is_ipad": False},
        "0x1292": {"type": "iPhone", "state": "DFU Mode", "is_ipad": False},
    }
    
    if product_id in pid_analysis:
        analysis = pid_analysis[product_id]
        device_info.update(analysis)
    
    # Additional analysis based on device name and instance ID
    if "ipad" in name:
        device_info["is_ipad"] = True
        device_info["device_type"] = "iPad"
    
    if "recovery" in name or "iboot" in name:
        device_info["state"] = "Recovery Mode"
    
    if "dfu" in name:
        device_info["state"] = "DFU Mode"
    
    # Extract additional info from instance ID
    if "CPID:" in instance_id:
        # Parse chip ID and other recovery mode info
        import re
        cpid_match = re.search(r'CPID:([0-9A-F]+)', instance_id)
        ecid_match = re.search(r'ECID:([0-9A-F]+)', instance_id)
        bdid_match = re.search(r'BDID:([0-9A-F]+)', instance_id)
        
        if cpid_match:
            device_info["chip_id"] = cpid_match.group(1)
        if ecid_match:
            device_info["ecid"] = ecid_match.group(1)
        if bdid_match:
            device_info["board_id"] = bdid_match.group(1)
    
    return device_info

def main():
    """Main function to find and display iPad information."""
    print("🔍 Searching for iPad devices (deduplicating interfaces)...")
    print("=" * 60)
    
    ipad_devices = find_ipad_devices()
    
    if not ipad_devices:
        print("❌ No iPad devices found.")
        print("\nTips:")
        print("- Make sure your iPad is connected via USB")
        print("- Try different USB cables/ports")
        print("- Check if the iPad appears in Device Manager")
        return
    
    print(f"✅ Found {len(ipad_devices)} Apple device(s):")
    print()
    
    for i, device in enumerate(ipad_devices, 1):
        print(f"📱 Device {i}:")
        print(f"   Type: {device['device_type']}")
        print(f"   State: {device['state']}")
        print(f"   Is iPad: {'✅ YES' if device['is_ipad'] else '❌ No'}")
        print(f"   Vendor ID: {device['original_device']['vendor_id']}")
        print(f"   Product ID: {device['original_device']['product_id']}")
        print(f"   Name: {device['original_device']['name']}")
        
        if device.get('chip_id'):
            print(f"   Chip ID: {device['chip_id']}")
        if device.get('ecid'):
            print(f"   ECID: {device['ecid']}")
        if device.get('board_id'):
            print(f"   Board ID: {device['board_id']}")
        
        print(f"   Instance ID: {device['original_device']['instance_id']}")
        print()
    
    # Find the actual iPad
    ipads = [d for d in ipad_devices if d['is_ipad']]
    if ipads:
        print("🎯 TARGET FOUND - iPad Device(s):")
        for ipad in ipads:
            print(f"   📱 {ipad['device_type']} in {ipad['state']}")
            print(f"   🔌 Vendor ID: {ipad['original_device']['vendor_id']}")
            print(f"   🔌 Product ID: {ipad['original_device']['product_id']}")
            print(f"   📋 Instance ID: {ipad['original_device']['instance_id']}")
    else:
        print("⚠️  Apple devices found, but none identified as iPad")

if __name__ == "__main__":
    main()