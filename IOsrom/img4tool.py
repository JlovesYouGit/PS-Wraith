#!/usr/bin/env python3
import struct
import sys
import os

class IMG4Tool:
    def __init__(self):
        self.magic = b'IMG4'
        
    def extract(self, img4_path, output_path):
        """Extract payload from IMG4 file"""
        try:
            with open(img4_path, 'rb') as f:
                data = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"IMG4 file not found: {img4_path}")
        except PermissionError:
            raise PermissionError(f"Permission denied reading: {img4_path}")
        
        # Find IMG4 magic
        if not data.startswith(self.magic):
            raise ValueError("Not a valid IMG4 file")
        
        # Skip IMG4 header and find payload
        offset = 4
        while offset < len(data) - 4:
            if data[offset:offset+4] == b'IM4P':
                # Found payload, extract it
                payload_start = offset + 4
                if payload_start + 4 > len(data):
                    raise ValueError("Malformed IMG4: insufficient data for payload size")
                
                # Find payload size (next 4 bytes after IM4P)
                payload_size = struct.unpack('>I', data[payload_start:payload_start+4])[0]
                
                if payload_size < 48:
                    raise ValueError("Invalid payload size in IMG4")
                
                # Skip to actual payload data (after ASN.1 headers)
                payload_offset = payload_start + 48  # Skip ASN.1 structure
                end_offset = payload_offset + payload_size - 48
                
                if end_offset > len(data):
                    raise ValueError("Malformed IMG4: payload extends beyond file")
                
                payload_data = data[payload_offset:end_offset]
                
                try:
                    with open(output_path, 'wb') as out:
                        out.write(payload_data)
                except PermissionError:
                    raise PermissionError(f"Permission denied writing to: {output_path}")
                
                print(f"Extracted payload to {output_path}")
                return
            offset += 1
        
        raise ValueError("No payload found in IMG4")
    
    def create(self, payload_path, output_path, fourcc=b'krnl'):
        """Create IMG4 from payload"""
        try:
            with open(payload_path, 'rb') as f:
                payload = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Payload file not found: {payload_path}")
        except PermissionError:
            raise PermissionError(f"Permission denied reading: {payload_path}")
        
        # Minimal IMG4 structure
        img4_header = self.magic + struct.pack('>I', len(payload) + 64)
        im4p_header = b'IM4P' + fourcc + struct.pack('>I', len(payload) + 48)
        
        # ASN.1 padding
        asn1_pad = b'\x30' + b'\x82' + struct.pack('>H', len(payload) + 32) + b'\x04' + struct.pack('>I', len(payload))
        
        try:
            with open(output_path, 'wb') as f:
                f.write(img4_header + im4p_header + asn1_pad + payload)
        except PermissionError:
            raise PermissionError(f"Permission denied writing to: {output_path}")
        
        print(f"Created IMG4: {output_path}")

def main():
    if len(sys.argv) < 4:
        print("Usage: python img4tool.py -extract <input> <output>")
        print("       python img4tool.py -create <payload> <output>")
        sys.exit(1)
    
    tool = IMG4Tool()
    
    try:
        if sys.argv[1] == '-extract':
            tool.extract(sys.argv[2], sys.argv[3])
        elif sys.argv[1] == '-create':
            tool.create(sys.argv[2], sys.argv[3])
        else:
            print("Unknown command")
            sys.exit(1)
    except (FileNotFoundError, PermissionError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()