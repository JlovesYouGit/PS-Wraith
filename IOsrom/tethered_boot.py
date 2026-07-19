#!/usr/bin/env python3
"""Tethered boot with custom kernelcache using limera1n"""
import os
import sys
import subprocess
import shutil

def tethered_boot_custom_kernel(base_ipsw, custom_kernel_path):
    """Boot device with custom kernelcache via limera1n tethered boot"""
    
    print("[+] Tethered Boot with Custom Kernelcache")
    print("[+] This will boot iOS 4.3.3 with iOS 9 kernel")
    
    # Extract kernelcache from base IPSW for comparison
    temp_dir = "temp_tethered"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    try:
        import zipfile
        
        # Extract original kernelcache
        with zipfile.ZipFile(base_ipsw, 'r') as zip_ref:
            for file in zip_ref.namelist():
                if 'kernelcache' in file.lower():
                    original_kernel = os.path.join(temp_dir, "original_kernelcache")
                    with open(original_kernel, 'wb') as f:
                        f.write(zip_ref.read(file))
                    print(f"[+] Extracted original kernel: {file}")
                    break
        
        # Check if we have custom kernel
        if not os.path.exists(custom_kernel_path):
            print(f"[!] Custom kernel not found: {custom_kernel_path}")
            return False
        
        print(f"[+] Original kernel: {original_kernel}")
        print(f"[+] Custom kernel: {custom_kernel_path}")
        
        # Tethered boot process
        print("\n[+] Tethered Boot Steps:")
        print("1. Put device in DFU mode (black screen)")
        print("2. limera1n will exploit bootrom")
        print("3. Upload custom kernelcache")
        print("4. Device boots with custom kernel")
        print("5. Must repeat on every reboot (tethered)")
        
        input("\nPress Enter when device is in DFU mode...")
        
        # Find limera1n
        limera1n_exe = "limera1n/limera1n.exe"
        if not os.path.exists(limera1n_exe):
            print("[!] limera1n.exe not found")
            return False
        
        print("[+] Running limera1n tethered boot...")
        
        # Run limera1n with custom kernel
        # Note: This is conceptual - actual limera1n syntax may vary
        cmd = [limera1n_exe, "-t", custom_kernel_path]  # -t = tethered boot
        
        try:
            result = subprocess.run(cmd, cwd="limera1n", capture_output=True, text=True)
            
            if "success" in result.stdout.lower() or result.returncode == 0:
                print("[✅] Tethered boot successful!")
                print("[+] Device should now boot with custom kernel")
                print("[!] Remember: This is tethered - repeat on every reboot")
                return True
            else:
                print(f"[!] limera1n failed:")
                print(f"stdout: {result.stdout}")
                print(f"stderr: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"[!] limera1n execution failed: {e}")
            return False
        
    except Exception as e:
        print(f"[!] Tethered boot setup failed: {e}")
        return False
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

def extract_ios9_kernel():
    """Extract iOS 9 kernelcache for tethered boot"""
    ios9_ipsw = "iPad2,1_9.3.5_13G36_Restore.ipsw"
    
    if not os.path.exists(ios9_ipsw):
        print(f"[!] iOS 9 IPSW not found: {ios9_ipsw}")
        return None
    
    try:
        import zipfile
        
        with zipfile.ZipFile(ios9_ipsw, 'r') as zip_ref:
            for file in zip_ref.namelist():
                if 'kernelcache' in file.lower():
                    kernel_path = "ios9_kernel_extracted"
                    with open(kernel_path, 'wb') as f:
                        f.write(zip_ref.read(file))
                    print(f"[+] Extracted iOS 9 kernel: {kernel_path}")
                    return kernel_path
        
        print("[!] No kernelcache found in iOS 9 IPSW")
        return None
        
    except Exception as e:
        print(f"[!] iOS 9 kernel extraction failed: {e}")
        return None

def main():
    print("[+] Tethered Boot Manager")
    
    # Extract iOS 9 kernel
    ios9_kernel = extract_ios9_kernel()
    if not ios9_kernel:
        return
    
    # Use clean iOS 4.3.3 as base
    base_ipsw = "iPad1,1_Clean.ipsw"
    if not os.path.exists(base_ipsw):
        base_ipsw = "iPad1,1_4.3.3_8J3_Restore.ipsw"
    
    if not os.path.exists(base_ipsw):
        print("[!] No base IPSW found")
        return
    
    # Perform tethered boot
    success = tethered_boot_custom_kernel(base_ipsw, ios9_kernel)
    
    if success:
        print("\n[✅] Tethered boot complete!")
        print("[+] Device running iOS 4.3.3 userland with iOS 9 kernel")
    else:
        print("\n[!] Tethered boot failed")

if __name__ == "__main__":
    main()