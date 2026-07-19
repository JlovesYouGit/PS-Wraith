#!/usr/bin/env python3
"""
Android Verified Boot (AVB) Bypass
Equivalent to iOS TSS/Signature bypass
"""
import os
import sys
import struct
import hashlib
from pathlib import Path
from typing import Dict, List, Optional

class AVBBypass:
    """Android Verified Boot bypass tools"""
    
    # AVB magic
    AVB_MAGIC = b"AVB0"
    
    # AVB footer offset from end of image
    AVB_FOOTER_OFFSET = 256
    
    def __init__(self):
        self.avb_disabled = False
    
    def read_avb_footer(self, image_path: str) -> Optional[Dict]:
        """Read AVB footer from boot/recovery image"""
        with open(image_path, 'rb') as f:
            f.seek(-self.AVB_FOOTER_OFFSET, 2)
            footer_data = f.read(self.AVB_FOOTER_OFFSET)
            
            magic = footer_data[:4]
            if magic != self.AVB_MAGIC:
                return None
            
            return {
                "magic": magic,
                "version": struct.unpack('<I', footer_data[4:8])[0],
                "original_image_size": struct.unpack('<Q', footer_data[8:16])[0],
                "algorithm": footer_data[16:48].rstrip(b'\x00').decode('utf-8'),
                "hash_offset": struct.unpack('<Q', footer_data[48:56])[0],
                "hash_size": struct.unpack('<Q', footer_data[56:64])[0],
                "signature_offset": struct.unpack('<Q', footer_data[64:72])[0],
                "signature_size": struct.unpack('<Q', footer_data[72:80])[0],
                "public_key_offset": struct.unpack('<I', footer_data[80:84])[0],
                "public_key_size": struct.unpack('<I', footer_data[84:88])[0],
                "public_key_metadata_offset": struct.unpack('<I', footer_data[88:92])[0],
                "public_key_metadata_size": struct.unpack('<I', footer_data[92:96])[0],
                "rollback_index": struct.unpack('<Q', footer_data[96:104])[0],
                "rollback_index_location": struct.unpack('<I', footer_data[104:108])[0],
                "flags": struct.unpack('<I', footer_data[108:112])[0],
            }
    
    def remove_avb_footer(self, image_path: str, output_path: str) -> Dict[str, any]:
        """Remove AVB footer and signature"""
        with open(image_path, 'rb') as f:
            data = f.read()
        
        footer = self.read_avb_footer(image_path)
        if not footer:
            return {"success": False, "error": "No AVB footer found"}
        
        # Remove footer and signature
        original_size = footer["original_image_size"]
        clean_data = data[:original_size]
        
        with open(output_path, 'wb') as f:
            f.write(clean_data)
        
        return {
            "success": True,
            "original_size": len(data),
            "clean_size": len(clean_data),
            "output": output_path
        }
    
    def patch_avb_footer(self, image_path: str, output_path: str,
                         disable_verification: bool = True,
                         set_rollback: int = 0) -> Dict[str, any]:
        """Patch AVB footer to disable verification"""
        with open(image_path, 'rb') as f:
            data = bytearray(f.read())
        
        footer = self.read_avb_footer(image_path)
        if not footer:
            return {"success": False, "error": "No AVB footer found"}
        
        footer_offset = len(data) - self.AVB_FOOTER_OFFSET
        
        if disable_verification:
            # Set hash size and signature size to 0
            struct.pack_into('<Q', data, footer_offset + 56, 0)
            struct.pack_into('<Q', data, footer_offset + 72, 0)
        
        if set_rollback is not None:
            # Set rollback index
            struct.pack_into('<Q', data, footer_offset + 96, set_rollback)
        
        with open(output_path, 'wb') as f:
            f.write(data)
        
        return {
            "success": True,
            "original_size": len(data),
            "output": output_path
        }
    
    def generate_avb_key(self, key_path: str) -> Dict[str, any]:
        """Generate AVB key pair"""
        try:
            # Use openssl to generate key
            subprocess.run(
                ["openssl", "genrsa", "-out", key_path, "2048"],
                check=True
            )
            return {"success": True, "key": key_path}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def sign_image(self, image_path: str, key_path: str, 
                   output_path: str) -> Dict[str, any]:
        """Sign boot image with custom key"""
        try:
            # Calculate hash
            with open(image_path, 'rb') as f:
                image_data = f.read()
            image_hash = hashlib.sha256(image_data).digest()
            
            # Sign hash
            sig_path = str(Path(output_path).with_suffix('.sig'))
            subprocess.run(
                ["openssl", "dgst", "-sha256", "-sign", key_path, "-out", sig_path, image_path],
                check=True
            )
            
            return {"success": True, "signature": sig_path}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def patch_boot_image_avb(self, boot_image_path: str, 
                             output_path: str) -> str:
        """Patch boot image to bypass AVB"""
        # Remove AVB footer
        result = self.remove_avb_footer(boot_image_path, output_path)
        if result.get("success"):
            return output_path
        
        # If no AVB footer, just copy
        import shutil
        shutil.copy2(boot_image_path, output_path)
        return output_path
    
    def get_avb_status(self, image_path: str) -> Dict[str, any]:
        """Get AVB status of image"""
        footer = self.read_avb_footer(image_path)
        if footer:
            return {
                "avb_enabled": True,
                "algorithm": footer.get("algorithm"),
                "rollback_index": footer.get("rollback_index"),
                "footer": footer
            }
        return {"avb_enabled": False}
