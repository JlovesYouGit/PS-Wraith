#!/usr/bin/env python
"""
Comprehensive iPad information extractor with all technical details.
"""
import json
import sys
import subprocess
import re
from typing import Optional, Dict, Any, List

def extract_detailed_info_from_instance_id(instance_id: str) -> Dict[str, Any]:
    """
    Extract all possible information from the USB instance ID.
    """
    info = {}
    
    # Extract Vendor ID and Product ID
    vid_match = re.search(r'VID_([0-9A-F]{4})', instance_id)
    pid_match = re.search(r'PID_([0-9A-F]{4})', instance_id)
    
    if vid_match:
        info["vendor_id"] = f"0x{vid_match.group(1)}"
    if pid_match:
        info["product_id"] = f"0x{pid_match.group(1)}"
    
    # Extract recovery mode specific information
    if "CPID:" in instance_id:
        # Chip ID
        cpid_match = re.search(r'CPID:([0-9A-F]+)', instance_id)
        if cpid_match:
            info["chip_id"] = cpid_match.group(1)
            info["chip_id_hex"] = f"0x{cpid_match.group(1)}"
            
            # Decode chip ID to processor name
            chip_names = {
                "8930": "A4 (iPad 1st Gen)",
                "8940": "A5 (iPad 2)",
                "8945": "A5 (iPad Mini 1st Gen)",
                "8950": "A6 (iPad 3rd Gen)",
                "8955": "A6X (iPad 4th Gen)",
                "8960": "A7 (iPad Air 1st Gen)",
                "8965": "A8 (iPad Mini 4)",
                "8001": "A8X (iPad Air 2)",
                "8011": "A9 (iPad 5th Gen)",
                "8027": "A9X (iPad Pro 1st Gen)",
                "8020": "A10 (iPad 6th Gen)",
                "8030": "A10X (iPad Pro 2nd Gen)",
                "8006": "A11 (iPad 7th Gen)",
                "8012": "A12 (iPad Air 3rd Gen)",
                "8028": "A12X/A12Z (iPad Pro 3rd/4th Gen)"
            }
            info["processor_name"] = chip_names.get(cpid_match.group(1), f"Unknown ({cpid_match.group(1)})")
    
    # Extract other recovery mode fields
    fields = {
        "CPRV": "chip_revision",
        "CPFM": "chip_fusing_mode", 
        "SCEP": "secure_epoch",
        "BDID": "board_id",
        "ECID": "ecid",
        "IBFL": "iboot_flags",
        "SRNM": "serial_number",
        "SRTG": "secure_rom_tag"
    }
    
    for field, key in fields.items():
        pattern = f"{field}:([0-9A-F]+)"
        match = re.search(pattern, instance_id)
        if match:
            info[key] = match.group(1)
            if key in ["board_id", "ecid"]:
                info[f"{key}_hex"] = f"0x{match.group(1)}"
    
    # Extract serial number from SRNM field (remove brackets)
    srnm_match = re.search(r'SRNM:\[([^\]]+)\]', instance_id)
    if srnm_match:
        info["serial_number"] = srnm_match.group(1)
    
    # Extract interface information
    mi_match = re.search(r'&MI_([0-9A-F]+)', instance_id)
    if mi_match:
        info["interface_number"] = mi_match.group(1)
        info["interface_number_decimal"] = str(int(mi_match.group(1), 16))
    
    return info

def get_all_ipad_details() -> List[Dict[str, Any]]:
    """
    Get comprehensive details for all iPad-related USB entries.
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
            
            detailed_devices = []
            for device in apple_devices:
                # Extract all available information
                detailed_info = {
                    "basic_info": {
                        "name": device.get("name", "Unknown"),
                        "device_class": device.get("device_class", "Unknown"),
                        "manufacturer": device.get("manufacturer", "Unknown"),
                        "status": device.get("status", "Unknown"),
                        "scan_type": device.get("scan_type", "Unknown"),
                        "method": device.get("method", "Unknown")
                    },
                    "usb_info": {
                        "vendor_id": device.get("vendor_id"),
                        "product_id": device.get("product_id"),
                        "instance_id": device.get("instance_id", "")
                    }
                }
                
                # Extract detailed technical information
                instance_id = device.get("instance_id", "")
                technical_info = extract_detailed_info_from_instance_id(instance_id)
                detailed_info["technical_info"] = technical_info
                
                # Determine device type and state
                device_analysis = analyze_device_type(device, technical_info)
                detailed_info["device_analysis"] = device_analysis
                
                detailed_devices.append(detailed_info)
            
            return detailed_devices
        
        return []
        
    except Exception as e:
        print(f"Error getting iPad details: {e}", file=sys.stderr)
        return []

def analyze_device_type(device: Dict[str, Any], technical_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze device type and state based on all available information.
    """
    analysis = {
        "device_type": "Unknown Apple Device",
        "device_state": "Unknown",
        "is_ipad": False,
        "confidence": "Low"
    }
    
    product_id = device.get("product_id", "")
    name = device.get("name", "").lower()
    
    # Product ID analysis
    if product_id == "0x1281":
        analysis["device_type"] = "iPad"
        analysis["device_state"] = "Recovery/DFU Mode"
        analysis["is_ipad"] = True
        analysis["confidence"] = "High"
    elif product_id == "0x1227":
        analysis["device_type"] = "iPad"
        analysis["device_state"] = "Recovery Mode (iBoot)"
        analysis["is_ipad"] = True
        analysis["confidence"] = "High"
    elif product_id in ["0x12A8", "0x12AB", "0x129A"]:
        analysis["device_type"] = "iPad"
        analysis["device_state"] = "Normal Mode"
        analysis["is_ipad"] = True
        analysis["confidence"] = "High"
    
    # Name-based analysis
    if "ipad" in name:
        analysis["device_type"] = "iPad"
        analysis["is_ipad"] = True
        analysis["confidence"] = "High"
    elif "recovery" in name or "iboot" in name:
        analysis["device_state"] = "Recovery Mode"
        if analysis["confidence"] == "Low":
            analysis["confidence"] = "Medium"
    
    # Chip ID analysis for iPad identification
    chip_id = technical_info.get("chip_id", "")
    if chip_id in ["8930", "8940", "8955", "8960", "8001", "8011", "8027", "8020", "8030", "8006", "8012", "8028"]:
        analysis["is_ipad"] = True
        if analysis["device_type"] == "Unknown Apple Device":
            analysis["device_type"] = "iPad"
        analysis["confidence"] = "High"
    
    return analysis

def print_detailed_info(devices: List[Dict[str, Any]]):
    """
    Print comprehensive device information in a readable format.
    """
    print("🔍 COMPREHENSIVE iPad USB INFORMATION")
    print("=" * 80)
    
    if not devices:
        print("❌ No Apple devices found!")
        return
    
    # Group devices by ECID (unique physical device)
    device_groups = {}
    for device in devices:
        ecid = device["technical_info"].get("ecid", "no_ecid")
        if ecid not in device_groups:
            device_groups[ecid] = []
        device_groups[ecid].append(device)
    
    print(f"📱 Found {len(device_groups)} unique physical device(s) with {len(devices)} USB interfaces")
    print()
    
    for group_id, (ecid, group_devices) in enumerate(device_groups.items(), 1):
        print(f"🎯 PHYSICAL DEVICE #{group_id}")
        print("=" * 50)
        
        # Use the most detailed device info (prefer recovery mode entries)
        primary_device = max(group_devices, key=lambda d: len(d["technical_info"]))
        
        # Basic Information
        print("📋 BASIC INFORMATION:")
        basic = primary_device["basic_info"]
        for key, value in basic.items():
            print(f"   {key.replace('_', ' ').title()}: {value}")
        
        print("\n🔌 USB INFORMATION:")
        usb = primary_device["usb_info"]
        print(f"   Vendor ID: {usb['vendor_id']} (Apple Inc.)")
        print(f"   Product ID: {usb['product_id']}")
        
        print("\n🔧 TECHNICAL DETAILS:")
        tech = primary_device["technical_info"]
        
        # Processor Information
        if tech.get("chip_id"):
            print(f"   Chip ID: {tech['chip_id']} ({tech.get('chip_id_hex', '')})")
            print(f"   Processor: {tech.get('processor_name', 'Unknown')}")
        
        if tech.get("chip_revision"):
            print(f"   Chip Revision: {tech['chip_revision']}")
        
        if tech.get("board_id"):
            print(f"   Board ID: {tech['board_id']} ({tech.get('board_id_hex', '')})")
        
        # Device Identifiers
        if tech.get("ecid"):
            print(f"   ECID: {tech['ecid']} ({tech.get('ecid_hex', '')})")
        
        if tech.get("serial_number"):
            print(f"   Serial Number: {tech['serial_number']}")
        
        # Security Information
        if tech.get("secure_epoch"):
            print(f"   Secure Epoch: {tech['secure_epoch']}")
        
        if tech.get("chip_fusing_mode"):
            print(f"   Chip Fusing Mode: {tech['chip_fusing_mode']}")
        
        if tech.get("iboot_flags"):
            print(f"   iBoot Flags: {tech['iboot_flags']}")
        
        if tech.get("secure_rom_tag"):
            print(f"   Secure ROM Tag: {tech['secure_rom_tag']}")
        
        print("\n📱 DEVICE ANALYSIS:")
        analysis = primary_device["device_analysis"]
        print(f"   Device Type: {analysis['device_type']}")
        print(f"   Device State: {analysis['device_state']}")
        print(f"   Is iPad: {'✅ YES' if analysis['is_ipad'] else '❌ No'}")
        print(f"   Confidence: {analysis['confidence']}")
        
        print("\n📋 USB INTERFACES:")
        for i, device in enumerate(group_devices, 1):
            interface_num = device["technical_info"].get("interface_number", "N/A")
            interface_dec = device["technical_info"].get("interface_number_decimal", "N/A")
            print(f"   Interface {i}: MI_{interface_num} (Decimal: {interface_dec})")
            print(f"      Name: {device['basic_info']['name']}")
            print(f"      Class: {device['basic_info']['device_class']}")
            print(f"      Instance ID: {device['usb_info']['instance_id']}")
        
        print("\n" + "=" * 50)
        print()

def export_to_json(devices: List[Dict[str, Any]], filename: str = "ipad_detailed_info.json"):
    """
    Export all detailed information to JSON file.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": __import__('datetime').datetime.now().isoformat(),
                "device_count": len(devices),
                "devices": devices
            }, f, indent=2, ensure_ascii=False)
        print(f"📄 Detailed information exported to: {filename}")
    except Exception as e:
        print(f"❌ Error exporting to JSON: {e}")

def main():
    """Main function."""
    print("🔍 Extracting comprehensive iPad information...")
    print()
    
    devices = get_all_ipad_details()
    
    if not devices:
        print("❌ No Apple devices found!")
        return 1
    
    # Print detailed information
    print_detailed_info(devices)
    
    # Export to JSON
    export_to_json(devices)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())