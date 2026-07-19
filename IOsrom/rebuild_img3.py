#!/usr/bin/env python3
"""Rebuild proper IMG3 container"""
import struct
import sys
import os

def rebuild_img3(payload_path, original_img3, output_path):
    """Rebuild IMG3 with new payload but preserve structure"""
    try:
        # Read new payload
        with open(payload_path, 'rb') as f:
            new_payload = f.read()
        
        # Read original IMG3 to get structure
        with open(original_img3, 'rb') as f:
            original_data = f.read()
        
        if not original_data.startswith(b'Img3'):
            print("[!] Original is not IMG3 format")
            return False
        
        # IMG3 structure: Img3 + size + data_size + signed_size + type + payload
        if len(original_data) < 20:
            print("[!] Original IMG3 too small")
            return False
        
        # Extract header info
        total_size = struct.unpack('<I', original_data[4:8])[0]
        data_size = struct.unpack('<I', original_data[8:12])[0] 
        signed_size = struct.unpack('<I', original_data[12:16])[0]
        img_type = original_data[16:20]
        
        # Build new IMG3
        new_total_size = 20 + len(new_payload)
        new_data_size = len(new_payload)
        
        new_img3 = (
            b'Img3' +                                    # Magic
            struct.pack('<I', new_total_size) +          # Total size
            struct.pack('<I', new_data_size) +           # Data size  
            struct.pack('<I', signed_size) +             # Keep original signed size
            img_type +                                   # Keep original type
            new_payload                                  # New payload
        )
        
        with open(output_path, 'wb') as f:
            f.write(new_img3)
        
        print(f"[✅] Rebuilt IMG3: {output_path}")
        return True
        
    except Exception as e:
        print(f"[!] IMG3 rebuild failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python rebuild_img3.py <payload> <original_img3> <output_img3>")
        sys.exit(1)
    
    success = rebuild_img3(sys.argv[1], sys.argv[2], sys.argv[3])
    sys.exit(0 if success else 1)