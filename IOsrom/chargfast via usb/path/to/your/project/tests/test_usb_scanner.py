import unittest
from unittest.mock import patch
from path.to.your.project.usb_scanner import scan_usb_devices, print_usb_devices

class TestUSBScanner(unittest.TestCase):
    @patch('usb.core.find')
    def test_scan_usb_devices(self, mock_find):
        mock_find.return_value = [
            MockUSBDevice(idVendor=0x1234, idProduct=0x5678, iProduct="Test Device"),
            MockUSBDevice(idVendor=0x9ABC, idProduct=0xDEF0, iProduct="Another Device")
        ]
        devices = scan_usb_devices()
        self.assertEqual(len(devices), 2)
        self.assertEqual(devices[0]["name"], "Test Device")
        self.assertEqual(devices[0]["vendor_id"], "0x1234")
        self.assertEqual(devices[0]["product_id"], "0x5678")
        self.assertEqual(devices[1]["name"], "Another Device")
        self.assertEqual(devices[1]["vendor_id"], "0x9ABC")
        self.assertEqual(devices[1]["product_id"], "0xDEF0")

    @patch('builtins.print')
    def test_print_usb_devices(self, mock_print):
        device_info = [
            {"name": "Test Device", "vendor_id": "0x1234", "product_id": "0x5678"},
            {"name": "Another Device", "vendor_id": "0x9ABC", "product_id": "0xDEF0"}
        ]
        print_usb_devices(device_info)
        mock_print.assert_any_call("Connected USB Devices:")
        mock_print.assert_any_call("- Name: Test Device")
        mock_print.assert_any_call("  Vendor ID: 0x1234")
        mock_print.assert_any_call("  Product ID: 0x5678")
        mock_print.assert_any_call("- Name: Another Device")
        mock_print.assert_any_call("  Vendor ID: 0x9ABC")
        mock_print.assert_any_call("  Product ID: 0xDEF0")

class MockUSBDevice:
    def __init__(self, idVendor, idProduct, iProduct):
        self.idVendor = idVendor
        self.idProduct = idProduct
        self.iProduct = iProduct
