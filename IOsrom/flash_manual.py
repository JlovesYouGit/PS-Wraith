#!/usr/bin/env python3
"""Manual flash instructions - Linux binaries won't run on Windows"""

print("""
[!] Linux binaries from Legacy iOS Kit are incompatible with Windows

[+] Manual Flash Options:

1. Use WSL (Windows Subsystem for Linux):
   - Install WSL: wsl --install
   - Copy Legacy iOS Kit to WSL
   - Run from WSL terminal

2. Use 3uTools:
   - Download 3uTools
   - Put device in DFU mode
   - Flash iPad1,1_iOS9_A4_Final.ipsw

3. Use iTunes + DFU mode:
   - Put device in DFU mode
   - Hold Shift + Restore in iTunes
   - Select iPad1,1_iOS9_A4_Final.ipsw

4. Build Windows idevicerestore:
   - Install MSYS2
   - Build from source in: 1.0.0 source code\\libimobiledevice-idevicerestore-a88351d

[+] Target IPSW: iPad1,1_iOS9_A4_Final.ipsw
[+] Device must be in DFU mode (black screen)
""")