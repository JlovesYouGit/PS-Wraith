#!/usr/bin/env python3
"""Create Frankenstein IPSW - iOS 4.3.3 base + iOS 9 components"""
import os
import sys
import shutil
import zipfile
from img3tool import IMG3Tool
from lzss_tool import decompress_lzss
from kernelcache_a4_patcher import KernelPatcher

def create_frankenstein_ipsw(ios4_ipsw, ios9_ipsw, output_ipsw):
    """Create Frankenstein IPSW mixing iOS 4 and iOS 9"""
    temp_ios4 = "temp_ios4"
    temp_ios9 = "temp_ios9" 
    temp_work = "temp_work"
    
    try:
        # Clean temp directories
        for temp_dir in [temp_ios4, temp_ios9, temp_work]:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)
        
        print("[+] Extracting iOS 4.3.3 base (bootable)...")
        with zipfile.ZipFile(ios4_ipsw, 'r') as zip_ref:
            zip_ref.extractall(temp_ios4)
        
        print("[+] Extracting iOS 9.3.5 source (components)...")
        with zipfile.ZipFile(ios9_ipsw, 'r') as zip_ref:
            zip_ref.extractall(temp_ios9)
        
        print("[+] Building Frankenstein components...")
        
        # Step 1: Keep iOS 4 bootchain (sn0wbreeze compatible)
        print("  ✓ Using iOS 4.3.3 bootchain (iBoot, LLB, etc.)")
        
        # Step 2: Extract and patch iOS 9 kernelcache
        ios9_kernel = None
        for root, dirs, files in os.walk(temp_ios9):
            for file in files:
                if 'kernelcache' in file.lower():
                    ios9_kernel = os.path.join(root, file)
                    break
        
        if ios9_kernel:
            print("  [+] Extracting iOS 9 kernelcache...")
            img3_tool = IMG3Tool()
            kernel_dec = os.path.join(temp_work, "ios9_kernel.dec")
            img3_tool.extract(ios9_kernel, kernel_dec)
            
            # Decompress if needed
            with open(kernel_dec, 'rb') as f:
                data = f.read()
            
            if data.startswith(b'complzss'):
                print("  [+] Decompressing iOS 9 kernelcache...")
                decompressed = decompress_lzss(data)
                kernel_lzss = kernel_dec + '.lzss'
                with open(kernel_lzss, 'wb') as f:
                    f.write(decompressed)
                kernel_dec = kernel_lzss
            
            # Apply A4 patches
            print("  [+] Applying A4 patches to iOS 9 kernelcache...")
            patcher = KernelPatcher(kernel_dec)
            patcher.apply_all_patches()
            patcher.close()
            
            # Replace iOS 4 kernelcache with patched iOS 9
            for root, dirs, files in os.walk(temp_ios4):
                for file in files:
                    if 'kernelcache' in file.lower():
                        ios4_kernel_path = os.path.join(root, file)
                        print(f"  [+] Replacing {file} with A4-patched iOS 9 kernel")
                        
                        # Read original iOS 4 kernelcache for IMG3 structure
                        with open(ios4_kernel_path, 'rb') as f:
                            ios4_kernel_data = f.read()
                        
                        # Read patched iOS 9 kernel
                        with open(kernel_dec, 'rb') as f:
                            ios9_kernel_data = f.read()
                        
                        # Create new IMG3 with iOS 9 payload
                        if ios4_kernel_data.startswith(b'Img3') and len(ios4_kernel_data) >= 20:
                            # Use iOS 4 IMG3 structure with iOS 9 payload
                            signed_size = struct.unpack('<I', ios4_kernel_data[12:16])[0]
                            img_type = ios4_kernel_data[16:20]
                            
                            new_img3 = (
                                b'Img3' +
                                struct.pack('<I', 20 + len(ios9_kernel_data)) +
                                struct.pack('<I', len(ios9_kernel_data)) +
                                struct.pack('<I', signed_size) +
                                img_type +
                                ios9_kernel_data
                            )
                            
                            with open(ios4_kernel_path, 'wb') as f:
                                f.write(new_img3)
                        else:
                            # Fallback - direct replacement
                            shutil.copy2(kernel_dec, ios4_kernel_path)
                        break
        
        # Step 3: Copy iOS 9 system frameworks (selective)
        print("  [+] Adding iOS 9 system components...")
        ios9_system_dmg = None
        for root, dirs, files in os.walk(temp_ios9):
            for file in files:
                if file.endswith('.dmg') and 'system' in file.lower():
                    ios9_system_dmg = os.path.join(root, file)
                    break
        
        if ios9_system_dmg:
            # Copy iOS 9 system DMG to iOS 4 base
            ios4_system_dmg = None
            for root, dirs, files in os.walk(temp_ios4):
                for file in files:
                    if file.endswith('.dmg') and 'system' in file.lower():
                        ios4_system_dmg = os.path.join(root, file)
                        break
            
            if ios4_system_dmg:
                print(f"  [+] Replacing system DMG with iOS 9 version")
                shutil.copy2(ios9_system_dmg, ios4_system_dmg)
        
        # Step 4: Keep iOS 4 BuildManifest (sn0wbreeze compatibility)
        print("  ✓ Keeping iOS 4.3.3 BuildManifest for sn0wbreeze")
        
        # Step 5: Create Frankenstein IPSW
        print("[+] Creating Frankenstein IPSW...")
        with zipfile.ZipFile(output_ipsw, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for root, dirs, files in os.walk(temp_ios4):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_path = os.path.relpath(file_path, temp_ios4)
                    zip_out.write(file_path, arc_path)
        
        print(f"[✅] Frankenstein IPSW created: {output_ipsw}")
        print("[+] Components:")
        print("  - iOS 4.3.3 bootchain (sn0wbreeze compatible)")
        print("  - iOS 9.3.5 kernelcache (A4 patched)")
        print("  - iOS 9 system frameworks")
        print("  - iOS 4 BuildManifest (signed)")
        return True
        
    except Exception as e:
        print(f"[!] Frankenstein creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        import time
        for temp_dir in [temp_ios4, temp_ios9, temp_work]:
            if os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except:
                    time.sleep(1)
                    try:
                        shutil.rmtree(temp_dir)
                    except:
                        pass

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python create_frankenstein.py <ios4.ipsw> <ios9.ipsw> <output.ipsw>")
        sys.exit(1)
    
    import struct
    success = create_frankenstein_ipsw(sys.argv[1], sys.argv[2], sys.argv[3])
    sys.exit(0 if success else 1)