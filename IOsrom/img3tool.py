#!/usr/bin/env python3
import struct
import sys

class IMG3Tool:
    def __init__(self):
        self.magic = b'Img3'
        
    def extract(self, img3_path, output_path):
        """Extract payload from IMG3 file or raw copy if not IMG3"""
        try:
            with open(img3_path, 'rb') as f:
                data = f.read()
        except (FileNotFoundError, PermissionError) as e:
            raise e
        
        # Check if it's actually IMG3 format
        if data.startswith(self.magic) and len(data) >= 20:
            # True IMG3 format
            data_size = struct.unpack('<I', data[8:12])[0]
            if 20 + data_size <= len(data):
                payload = data[20:20 + data_size]
            else:
                # Fallback to raw copy
                payload = data
        else:
            # Not IMG3 or malformed - do raw copy
            payload = data
        
        try:
            with open(output_path, 'wb') as f:
                f.write(payload)
        except PermissionError as e:
            raise e
        
        print(f"Extracted payload to {output_path}")

def main():
    if len(sys.argv) != 4 or sys.argv[1] != '-extract':
        print("Usage: python img3tool.py -extract <input> <output>")
        sys.exit(1)
    
    try:
        tool = IMG3Tool()
        tool.extract(sys.argv[2], sys.argv[3])
    except (FileNotFoundError, PermissionError) as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()