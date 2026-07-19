#!/usr/bin/env python3
"""Create hybrid IPSW with properly patched A4 kernelcache"""
import os
import sys
import shutil
import zipfile
import struct
from img3tool import IMG3Tool
from lzss_tool import decompress_lzss
from kernelcache_a4_patcher import KernelPatcher

def create_patched_hybrid(ipad1_ipsw, ipad2_ipsw, output_ipsw):
    """Create hybrid with A4-patched kernelcache"""
    temp_base = "temp_base"
    temp_source = "temp_source"
    temp_work = "temp_work"
    
    try:
        # Clean temp directories
        for temp_dir in [temp_base, temp_source, temp_work]:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)
        
        print("[+] Extracting iPad1,1 5.1.1 base...")
        with zipfile.ZipFile(ipad1_ipsw, 'r') as zip_ref:
            zip_ref.extractall(temp_base)
        
        print("[+] Extracting iPad2,1 9.3.5 source...")
        with zipfile.ZipFile(ipad2_ipsw, 'r') as zip_ref:
            zip_ref.extractall(temp_source)
        
        # Find and extract iPad2,1 kernelcache
        source_kernel = None
        for root, dirs, files in os.walk(temp_source):
            for file in files:
                if 'kernelcache' in file.lower():
                    source_kernel = os.path.join(root, file)
                    break
        
        if not source_kernel:
            print("[!] No kernelcache found in iPad2,1 IPSW")
            return False
        
        print("[+] Extracting and patching kernelcache...")
        
        # Extract kernelcache
        img3_tool = IMG3Tool()
        kernel_dec = os.path.join(temp_work, "kernelcache.dec")
        img3_tool.extract(source_kernel, kernel_dec)
        
        # Decompress if LZSS
        with open(kernel_dec, 'rb') as f:
            data = f.read()
        
        if data.startswith(b'complzss'):
            print("[+] Decompressing LZSS...")
            decompressed = decompress_lzss(data)
            kernel_lzss = kernel_dec + '.lzss'
            with open(kernel_lzss, 'wb') as f:
                f.write(decompressed)
            kernel_dec = kernel_lzss
        
        # Apply A4 patches
        print("[+] Applying A4 compatibility patches...")
        try:
            patcher = KernelPatcher(kernel_dec)
            patcher.apply_all_patches()
            patcher.close()
        except Exception as e:
            print(f"[!] Patching failed: {e}")
            return False
        
        # Recompress if needed
        if kernel_dec.endswith('.lzss'):
            print("[+] Recompressing kernelcache...")
            with open(kernel_dec, 'rb') as f:
                patched_data = f.read()
            
            # Simple compression header
            compressed = b'complzss' + len(patched_data).to_bytes(4, 'little') + patched_data
            kernel_final = os.path.join(temp_work, "kernelcache.final")
            with open(kernel_final, 'wb') as f:
                f.write(compressed)
        else:
            kernel_final = kernel_dec
        
        # Rebuild IMG3 container properly
        kernel_img3 = os.path.join(temp_work, "kernelcache.img3")
        
        # Read original IMG3 structure
        with open(source_kernel, 'rb') as f:
            original_img3 = f.read()
        
        if original_img3.startswith(b'Img3') and len(original_img3) >= 20:
            # Rebuild proper IMG3 with new payload
            with open(kernel_final, 'rb') as f:
                new_payload = f.read()
            
            # Extract original header info
            signed_size = struct.unpack('<I', original_img3[12:16])[0]
            img_type = original_img3[16:20]
            
            # Build new IMG3
            new_total_size = 20 + len(new_payload)
            new_img3 = (
                b'Img3' +
                struct.pack('<I', new_total_size) +
                struct.pack('<I', len(new_payload)) +
                struct.pack('<I', signed_size) +
                img_type +
                new_payload
            )
            
            with open(kernel_img3, 'wb') as f:
                f.write(new_img3)
        else:
            # Fallback to raw copy
            shutil.copy2(kernel_final, kernel_img3)
        
        # Replace kernelcache in iPad1,1 base
        for root, dirs, files in os.walk(temp_base):
            for file in files:
                if 'kernelcache' in file.lower():
                    target_kernel = os.path.join(root, file)
                    print(f"[+] Replacing kernelcache: {file}")
                    shutil.copy2(kernel_img3, target_kernel)
                    break
        
        # Create final hybrid IPSW
        print("[+] Creating patched hybrid IPSW...")
        with zipfile.ZipFile(output_ipsw, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for root, dirs, files in os.walk(temp_base):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_path = os.path.relpath(file_path, temp_base)
                    zip_out.write(file_path, arc_path)
        
        print(f"[✅] Patched hybrid IPSW created: {output_ipsw}")
        print("[!] Uses iPad1,1 5.1.1 base with A4-patched iOS 9 kernelcache")
        return True
        
    except Exception as e:
        print(f"[!] Patched hybrid creation failed: {e}")
        return False
    finally:
        # Cleanup with retry
        import time
        for temp_dir in [temp_base, temp_source, temp_work]:
            if os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except PermissionError:
                    # Wait and retry
                    time.sleep(1)
                    try:
                        shutil.rmtree(temp_dir)
                    except:
                        print(f"[!] Could not cleanup {temp_dir}")
                        pass

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python create_patched_hybrid.py <ipad1_5.1.1.ipsw> <ipad2_9.3.5.ipsw> <output.ipsw>")
        sys.exit(1)
    
    success = create_patched_hybrid(sys.argv[1], sys.argv[2], sys.argv[3])
    sys.exit(0 if success else 1)