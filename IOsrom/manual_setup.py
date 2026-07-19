#!/usr/bin/env python3
"""Manual setup instructions"""
print("""
[+] Manual Setup Instructions:

1. Download ipwndfu:
   - Go to: https://github.com/axi0mX/ipwndfu
   - Download ZIP and extract to 'ipwndfu-win32' folder

2. Download secureboot_tools:
   - Go to: https://github.com/dora2-iOS/secureboot_tools  
   - Download ZIP and extract to 'secureboot_tools' folder

3. Install pyusb:
   pip install pyusb

4. Install DFU driver:
   - Download Zadig from https://zadig.akeo.ie/
   - Put device in DFU mode
   - In Zadig, select Apple Mobile Device (DFU Mode)
   - Install libusbK driver

5. Extract IPSW:
   python extract_ipsw_parts.py

6. Flash:
   python flash_raw.py
""")