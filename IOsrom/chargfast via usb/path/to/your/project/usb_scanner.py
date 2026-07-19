#!/usr/bin/env python
import usb.core
import usb.util

def scan_usb_devices(max_devices=None):
    """Scan for all connected USB devices and return a list of device information."""
    devices = usb.core.find(find_all=True, max_devices=max_devices)
    if not devices:
        return []

    device_info = []
    for device in devices:
        try:
            device_name = usb.util.get_string(device, device.iProduct)
        except usb.util.USBError:
            device_name = "Unknown"
        vendor_id = f"0x{device.idVendor:04X}"
        product_id = f"0x{device.idProduct:04X}"
        device_info.append({
            "name": device_name,
            "vendor_id": vendor_id,
            "product_id": product_id
        })
    return device_info

def print_usb_devices(device_info):
    """Print the information for a list of USB devices."""
    print("Connected USB Devices:")
    for device in device_info:
        print(f"- Name: {device['name']}")
        print(f"  Vendor ID: {device['vendor_id']}")
        print(f"  Product ID: {device['product_id']}")

if __name__ == "__main__":
    device_info = scan_usb_devices()
    print_usb_devices(device_info)
