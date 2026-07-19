#!/usr/bin/env python3
"""Fix DFU mode detection and device communication"""
import subprocess
import time

def check_dfu_device():
    """Check if device is properly detected in DFU mode"""
    print("[+] Checking DFU device detection...")
    
    # Check Windows device manager
    try:
        result = subprocess.run(['wmic', 'path', 'win32_pnpentity', 'where', 
                               'name like "%Apple%"', 'get', 'name'], 
                               capture_output=True, text=True)
        
        if "Apple Recovery (DFU) USB Driver" in result.stdout:
            print("[✅] Device detected in DFU mode")
            return True
        elif "Apple Mobile Device (DFU Mode)" in result.stdout:
            print("[✅] Device detected in DFU mode (alternative driver)")
            return True
        else:
            print("[!] Device not detected in DFU mode")
            print("Detected Apple devices:")
            for line in result.stdout.split('\n'):
                if 'Apple' in line and line.strip():
                    print(f"  {line.strip()}")
            return False
            
    except Exception as e:
        print(f"[!] Device check failed: {e}")
        return False

def fix_dfu_mode():
    """Guide user to proper DFU mode"""
    print("[+] DFU Mode Instructions:")
    print("=" * 30)
    print("1. Hold Home + Power buttons for 10 seconds")
    print("2. Release Power button, keep holding Home")
    print("3. Hold Home for 10 more seconds")
    print("4. Screen should be COMPLETELY BLACK")
    print("5. Windows should detect 'Apple Recovery (DFU) USB Driver'")
    print()
    
    for i in range(3):
        print(f"Attempt {i+1}/3:")
        input("Press Enter when device is in DFU mode...")
        
        if check_dfu_device():
            return True
        
        print("[!] DFU mode not detected, try again")
        time.sleep(2)
    
    return False

def try_different_usb():
    """Try different USB configurations"""
    print("[+] USB Troubleshooting:")
    print("- Try USB 2.0 port (not USB 3.0)")
    print("- Use different USB cable")
    print("- Connect to back USB ports")
    print("- Try different computer if available")
    print("- Disable USB 3.0 in BIOS temporarily")
    
    input("Press Enter after trying different USB setup...")
    return check_dfu_device()

def manual_limera1n():
    """Run limera1n manually"""
    print("[+] Running limera1n manually...")
    
    limera1n_exe = "limera1n/limera1n.exe"
    if not os.path.exists(limera1n_exe):
        print("[!] limera1n.exe not found")
        return False
    
    print("1. Put device in DFU mode")
    print("2. Run limera1n.exe manually")
    print("3. Click 'make it ra1n' when device detected")
    
    try:
        # Launch limera1n GUI
        subprocess.Popen([limera1n_exe], cwd="limera1n")
        print("[+] limera1n launched - use GUI to exploit device")
        return True
    except Exception as e:
        print(f"[!] limera1n launch failed: {e}")
        return False

def main():
    """Fix DFU detection issues"""
    print("[+] DFU Mode Detection Fixer")
    print("=" * 40)
    
    # Step 1: Check current detection
    if check_dfu_device():
        print("[✅] Device already detected in DFU mode")
        return True
    
    # Step 2: Guide proper DFU mode
    if fix_dfu_mode():
        print("[✅] DFU mode fixed")
        return True
    
    # Step 3: Try different USB
    print("\n[+] Trying USB troubleshooting...")
    if try_different_usb():
        print("[✅] USB issue resolved")
        return True
    
    # Step 4: Manual limera1n
    print("\n[+] Trying manual limera1n...")
    if manual_limera1n():
        print("[✅] Use limera1n GUI manually")
        return True
    
    print("\n[!] DFU detection failed")
    print("Try:")
    print("- Different iPad if available")
    print("- Different computer")
    print("- Check USB cable")
    
    return False

if __name__ == "__main__":
    import os
    main()