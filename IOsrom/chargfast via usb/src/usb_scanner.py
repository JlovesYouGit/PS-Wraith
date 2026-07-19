#!/usr/bin/env python
import json
import sys
import argparse
import re
import datetime
from typing import List, Dict, Any

def scan_usb_with_pyusb() -> List[Dict[str, Any]]:
    """
    Scan USB devices using PyUSB library.
    """
    try:
        import usb.core
        import usb.util
        
        devices = usb.core.find(find_all=True)
        usb_devices = []
        
        for device in devices:
            try:
                device_info = {
                    "vendor_id": f"0x{device.idVendor:04x}",
                    "product_id": f"0x{device.idProduct:04x}",
                    "device_class": device.bDeviceClass,
                    "device_subclass": device.bDeviceSubClass,
                    "device_protocol": device.bDeviceProtocol,
                    "bus": device.bus,
                    "address": device.address,
                    "speed": getattr(device, 'speed', 'unknown'),
                    "manufacturer": None,
                    "product": None,
                    "serial_number": None
                }
                
                # Try to get string descriptors
                try:
                    if device.iManufacturer:
                        device_info["manufacturer"] = usb.util.get_string(device, device.iManufacturer)
                except:
                    pass
                    
                try:
                    if device.iProduct:
                        device_info["product"] = usb.util.get_string(device, device.iProduct)
                except:
                    pass
                    
                try:
                    if device.iSerialNumber:
                        device_info["serial_number"] = usb.util.get_string(device, device.iSerialNumber)
                except:
                    pass
                
                usb_devices.append(device_info)
                
            except Exception as e:
                # Add device with error info
                usb_devices.append({
                    "vendor_id": f"0x{device.idVendor:04x}",
                    "product_id": f"0x{device.idProduct:04x}",
                    "error": str(e)
                })
        
        return usb_devices
        
    except Exception as e:
        raise Exception(f"PyUSB error: {str(e)}")

def scan_usb_with_powershell() -> List[Dict[str, Any]]:
    """
    Scan USB devices using PowerShell Get-PnpDevice (Windows 10/11).
    """
    try:
        import subprocess
        
        # Simple PowerShell command to get USB devices
        cmd = [
            "powershell", "-Command",
            "Get-PnpDevice | Where-Object { $_.InstanceId -like '*USB*' -and $_.Status -eq 'OK' } | Select-Object FriendlyName, InstanceId, Class, Manufacturer, Status | ConvertTo-Json"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, shell=False)
        
        if result.returncode == 0 and result.stdout.strip():
            try:
                ps_data = json.loads(result.stdout)
                if not isinstance(ps_data, list):
                    ps_data = [ps_data] if ps_data else []
                
                usb_devices = []
                for device in ps_data:
                    device_info = {
                        "name": device.get("FriendlyName", "Unknown"),
                        "instance_id": device.get("InstanceId", "Unknown"),
                        "device_class": device.get("Class", "Unknown"),
                        "manufacturer": device.get("Manufacturer", "Unknown"),
                        "status": device.get("Status", "Unknown"),
                        "method": "PowerShell"
                    }
                    
                    # Extract VID and PID from InstanceId
                    instance_id = device.get("InstanceId", "")
                    if "VID_" in instance_id and "PID_" in instance_id:
                        try:
                            vid_match = re.search(r'VID_([0-9A-F]{4})', instance_id)
                            pid_match = re.search(r'PID_([0-9A-F]{4})', instance_id)
                            
                            if vid_match:
                                device_info["vendor_id"] = f"0x{vid_match.group(1)}"
                            if pid_match:
                                device_info["product_id"] = f"0x{pid_match.group(1)}"
                        except:
                            pass
                    
                    usb_devices.append(device_info)
                
                return usb_devices
            except json.JSONDecodeError as e:
                raise Exception(f"JSON parsing error: {str(e)}")
        else:
            raise Exception(f"PowerShell command failed with return code {result.returncode}. Error: {result.stderr}")
        
    except Exception as e:
        raise Exception(f"PowerShell error: {str(e)}")

def scan_usb_with_wmi() -> List[Dict[str, Any]]:
    """
    Scan USB devices using Windows WMI (Windows Management Instrumentation).
    """
    try:
        import subprocess
        
        # Use PowerShell to query WMI for USB devices
        cmd = [
            "powershell", "-Command",
            "Get-CimInstance -ClassName Win32_USBControllerDevice | ForEach-Object { Get-CimInstance -ClassName Win32_PnPEntity -Filter \"DeviceID='$($_.Dependent.DeviceID)'\" } | Where-Object { $_.DeviceID -like '*USB*' } | Select-Object Name, DeviceID, Manufacturer, Service | ConvertTo-Json"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, shell=False)
        
        if result.returncode == 0 and result.stdout.strip():
            try:
                wmi_data = json.loads(result.stdout)
                if not isinstance(wmi_data, list):
                    wmi_data = [wmi_data] if wmi_data else []
                
                usb_devices = []
                for device in wmi_data:
                    device_info = {
                        "name": device.get("Name", "Unknown"),
                        "device_id": device.get("DeviceID", "Unknown"),
                        "manufacturer": device.get("Manufacturer", "Unknown"),
                        "service": device.get("Service", "Unknown"),
                        "method": "WMI"
                    }
                    
                    # Extract VID and PID from DeviceID if possible
                    device_id = device.get("DeviceID", "")
                    if "VID_" in device_id and "PID_" in device_id:
                        try:
                            vid_start = device_id.find("VID_") + 4
                            vid_end = device_id.find("&", vid_start)
                            if vid_end == -1:
                                vid_end = device_id.find("\\", vid_start)
                            if vid_end == -1:
                                vid_end = vid_start + 4
                            
                            pid_start = device_id.find("PID_") + 4
                            pid_end = device_id.find("&", pid_start)
                            if pid_end == -1:
                                pid_end = device_id.find("\\", pid_start)
                            if pid_end == -1:
                                pid_end = pid_start + 4
                            
                            device_info["vendor_id"] = f"0x{device_id[vid_start:vid_end]}"
                            device_info["product_id"] = f"0x{device_id[pid_start:pid_end]}"
                        except:
                            pass
                    
                    usb_devices.append(device_info)
                
                return usb_devices
            except json.JSONDecodeError:
                raise Exception("Failed to parse WMI JSON output")
        else:
            raise Exception(f"WMI command failed with return code {result.returncode}")
        
    except Exception as e:
        raise Exception(f"WMI error: {str(e)}")

def list_usb_devices(output_format: str = "json", verbose: bool = False) -> None:
    """
    Scan for all connected USB devices and output their information.
    
    Args:
        output_format: Output format ('json' or 'text')
        verbose: Include verbose error information
    """
    usb_devices = []
    errors = []
    method_used = "None"
    
    # Try PyUSB first
    try:
        usb_devices = scan_usb_with_pyusb()
        method_used = "PyUSB"
    except Exception as e:
        errors.append(f"PyUSB method failed: {str(e)}")
        
        # Fallback to PowerShell on Windows
        try:
            usb_devices = scan_usb_with_powershell()
            method_used = "PowerShell"
        except Exception as e2:
            errors.append(f"PowerShell method failed: {str(e2)}")
            
            # Final fallback to WMI
            try:
                usb_devices = scan_usb_with_wmi()
                method_used = "WMI"
            except Exception as e3:
                errors.append(f"WMI method failed: {str(e3)}")
    
    # Prepare output
    output_data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "method": method_used if usb_devices else "None",
        "device_count": len(usb_devices),
        "devices": usb_devices
    }
    
    if verbose and errors:
        output_data["errors"] = errors
    
    if output_format.lower() == "json":
        print(json.dumps(output_data, indent=2, ensure_ascii=False))
    else:
        # Text format
        print(f"USB Device Scanner - {output_data['timestamp']}")
        print(f"Method: {output_data['method']}")
        print(f"Found {output_data['device_count']} USB devices:")
        print("-" * 50)
        
        for i, device in enumerate(usb_devices, 1):
            print(f"\nDevice {i}:")
            for key, value in device.items():
                if value is not None:
                    print(f"  {key.replace('_', ' ').title()}: {value}")
        
        if verbose and errors:
            print("\nErrors encountered:")
            for error in errors:
                print(f"  - {error}")

def filter_devices(devices: List[Dict[str, Any]], filter_type: str) -> List[Dict[str, Any]]:
    """
    Filter devices based on type (apple, ipad, iphone, etc.)
    """
    if not filter_type:
        return devices
    
    filter_type = filter_type.lower()
    filtered = []
    
    # Apple device identification
    apple_vendor_ids = ["0x05AC"]  # Apple Inc. Vendor ID
    apple_keywords = ["apple", "ipad", "iphone", "ipod", "mac"]
    
    for device in devices:
        device_match = False
        
        if filter_type == "apple":
            # Check vendor ID
            if device.get("vendor_id") in apple_vendor_ids:
                device_match = True
            # Check device name/manufacturer for Apple keywords
            name = device.get("name", "").lower()
            manufacturer = device.get("manufacturer", "").lower()
            if any(keyword in name or keyword in manufacturer for keyword in apple_keywords):
                device_match = True
                
        elif filter_type == "ipad":
            # Specific iPad detection
            name = device.get("name", "").lower()
            if "ipad" in name or (device.get("vendor_id") == "0x05AC" and "ipad" in name):
                device_match = True
                
        elif filter_type == "iphone":
            # Specific iPhone detection
            name = device.get("name", "").lower()
            if "iphone" in name or (device.get("vendor_id") == "0x05AC" and "iphone" in name):
                device_match = True
                
        else:
            # Generic keyword search
            search_fields = [
                device.get("name", ""),
                device.get("manufacturer", ""),
                device.get("device_class", ""),
                device.get("instance_id", "")
            ]
            if any(filter_type in field.lower() for field in search_fields):
                device_match = True
        
        if device_match:
            filtered.append(device)
    
    return filtered

def scan_for_apple_devices() -> List[Dict[str, Any]]:
    """
    Enhanced scan specifically looking for Apple devices including those that might not show up in standard scans.
    """
    try:
        import subprocess
        
        # Enhanced PowerShell command to find Apple devices
        cmd = [
            "powershell", "-Command",
            """
            # Get all USB devices including those that might be hidden
            $allDevices = @()
            
            # Standard PnP devices
            $pnpDevices = Get-PnpDevice | Where-Object { 
                $_.InstanceId -like '*USB*' -or 
                $_.InstanceId -like '*VID_05AC*' -or
                $_.FriendlyName -like '*Apple*' -or
                $_.FriendlyName -like '*iPad*' -or
                $_.FriendlyName -like '*iPhone*'
            }
            
            foreach ($device in $pnpDevices) {
                $allDevices += [PSCustomObject]@{ 
                    FriendlyName = $device.FriendlyName
                    InstanceId = $device.InstanceId
                    Class = $device.Class
                    Manufacturer = $device.Manufacturer
                    Status = $device.Status
                    Type = "PnP"
                }
            }
            
            # Also check WMI for additional devices
            try {
                $wmiDevices = Get-CimInstance -ClassName Win32_PnPEntity | Where-Object { 
                    $_.DeviceID -like '*VID_05AC*' -or
                    $_.Name -like '*Apple*' -or
                    $_.Name -like '*iPad*' -or
                    $_.Name -like '*iPhone*'
                }
                
                foreach ($device in $wmiDevices) {
                    $allDevices += [PSCustomObject]@{ 
                        FriendlyName = $device.Name
                        InstanceId = $device.DeviceID
                        Class = $device.PNPClass
                        Manufacturer = $device.Manufacturer
                        Status = $device.Status
                        Type = "WMI"
                    }
                }
            } catch {}
            
            $allDevices | ConvertTo-Json -Depth 3
            """
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, shell=False)
        
        if result.returncode == 0 and result.stdout.strip():
            try:
                ps_data = json.loads(result.stdout)
                if not isinstance(ps_data, list):
                    ps_data = [ps_data] if ps_data else []
                
                apple_devices = []
                for device in ps_data:
                    device_info = {
                        "name": device.get("FriendlyName", "Unknown"),
                        "instance_id": device.get("InstanceId", "Unknown"),
                        "device_class": device.get("Class", "Unknown"),
                        "manufacturer": device.get("Manufacturer", "Unknown"),
                        "status": device.get("Status", "Unknown"),
                        "scan_type": device.get("Type", "Unknown"),
                        "method": "Enhanced Apple Scan"
                    }
                    
                    # Extract VID and PID
                    instance_id = device.get("InstanceId", "")
                    if "VID_" in instance_id and "PID_" in instance_id:
                        try:
                            vid_match = re.search(r'VID_([0-9A-F]{4})', instance_id)
                            pid_match = re.search(r'PID_([0-9A-F]{4})', instance_id)
                            
                            if vid_match:
                                device_info["vendor_id"] = f"0x{vid_match.group(1)}"
                            if pid_match:
                                device_info["product_id"] = f"0x{pid_match.group(1)}"
                        except:
                            pass
                    
                    apple_devices.append(device_info)
                
                return apple_devices
            except json.JSONDecodeError:
                return []
        
        return []
        
    except Exception:
        return []

def check_ios_recovery_mode() -> Dict[str, Any]:
    """
    Check if there's an iOS device in recovery mode using irecovery.
    """
    try:
        from pathlib import Path
        
        # Find irecovery
        current_dir = Path.cwd()
        irecovery_exe = current_dir / "irecovery.exe"
        
        if not irecovery_exe.exists():
            return {"available": False, "reason": "irecovery.exe not found"}
        
        # Test connection
        result = subprocess.run([
            str(irecovery_exe), "-q"
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            # Parse device info
            info = {}
            for line in result.stdout.split('\n'):
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    info[key.strip().lower().replace(' ', '_')] = value.strip()
            
            return {
                "available": True,
                "connected": True,
                "device_info": info,
                "tool": "irecovery"
            }
        else:
            return {
                "available": True,
                "connected": False,
                "error": result.stderr.strip() if result.stderr else "No device found"
            }
            
    except Exception as e:
        return {"available": False, "reason": str(e)}

def main():
    """Main entry point with command line argument parsing."""
    parser = argparse.ArgumentParser(description="USB Device Scanner with iOS Recovery Support")
    parser.add_argument(
        "--format", "-f", 
        choices=["json", "text"],
        default="json",
        help="Output format (default: json)"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true",
        help="Include verbose error information"
    )
    parser.add_argument(
        "--filter", 
        help="Filter devices by type (apple, ipad, iphone) or keyword"
    )
    parser.add_argument(
        "--apple-scan", 
        action="store_true",
        help="Enhanced scan specifically for Apple devices"
    )
    parser.add_argument(
        "--ios-recovery", 
        action="store_true",
        help="Check for iOS devices in recovery mode using irecovery"
    )
    
    args = parser.parse_args()
    
    try:
        if args.ios_recovery:
            # Check for iOS devices in recovery mode
            recovery_info = check_ios_recovery_mode()
            
            if args.format.lower() == "json":
                print(json.dumps({
                    "timestamp": datetime.datetime.now().isoformat(),
                    "method": "iOS Recovery Check",
                    "recovery_mode": recovery_info
                }, indent=2, ensure_ascii=False))
            else:
                print(f"iOS Recovery Mode Check - {datetime.datetime.now().isoformat()}")
                print("-" * 50)
                
                if recovery_info.get("available"):
                    if recovery_info.get("connected"):
                        print("✅ iOS device found in recovery mode!")
                        device_info = recovery_info.get("device_info", {})
                        for key, value in device_info.items():
                            print(f"  {key.replace('_', ' ').title()}: {value}")
                        print("\n🔧 To fix auto-boot issue, run: python fix_auto_boot.py")
                    else:
                        print(f"❌ No iOS device in recovery mode: {recovery_info.get('error', 'Unknown')}")
                else:
                    print(f"❌ irecovery not available: {recovery_info.get('reason', 'Unknown')}")
                    
        elif args.apple_scan:
            # Enhanced Apple device scan
            apple_devices = scan_for_apple_devices()
            
            # Also check recovery mode
            recovery_info = check_ios_recovery_mode()
            
            output_data = {
                "timestamp": datetime.datetime.now().isoformat(),
                "method": "Enhanced Apple Scan",
                "device_count": len(apple_devices),
                "devices": apple_devices,
                "recovery_mode": recovery_info
            }
            
            if args.format.lower() == "json":
                print(json.dumps(output_data, indent=2, ensure_ascii=False))
            else:
                print(f"Apple Device Scanner - {output_data['timestamp']}")
                print(f"Found {output_data['device_count']} Apple devices:")
                print("-" * 50)
                
                for i, device in enumerate(apple_devices, 1):
                    print(f"\nDevice {i}:")
                    for key, value in device.items():
                        if value is not None:
                            print(f"  {key.replace('_', ' ').title()}: {value}")
                
                # Show recovery mode info
                print("\niOS Recovery Mode Status:")
                if recovery_info.get("available"):
                    if recovery_info.get("connected"):
                        print("✅ iOS device in recovery mode detected!")
                        print("🔧 Run 'python fix_auto_boot.py' to fix charging issues")
                    else:
                        print("ℹ️  No device in recovery mode")
                else:
                    print("ℹ️  irecovery not available for recovery mode detection")
        else:
            # Standard scan with optional filtering
            list_usb_devices(args.format, args.verbose)
            
    except KeyboardInterrupt:
        print("\nScan interrupted by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        error_output = {
            "error": "Fatal error occurred",
            "message": str(e),
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        if args.format == "json":
            print(json.dumps(error_output, indent=2), file=sys.stderr)
        else:
            print(f"Error: {str(e)}", file=sys.stderr)
        
        sys.exit(1)

if __name__ == "__main__":
    main()