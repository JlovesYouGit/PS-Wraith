#!/usr/bin/env python3
import struct
import sys

def decompress_lzss(data):
    """Decompress LZSS compressed data (iOS kernelcache format)"""
    if len(data) < 12:
        return data
    
    # Check for complzss header
    if data[:8] != b'complzss':
        return data
    
    # Get decompressed size
    decomp_size = struct.unpack('<I', data[8:12])[0]
    compressed_data = data[12:]
    
    output = bytearray()
    src_pos = 0
    
    while src_pos < len(compressed_data) and len(output) < decomp_size:
        # Read control byte
        if src_pos >= len(compressed_data):
            break
        control = compressed_data[src_pos]
        src_pos += 1
        
        for i in range(8):
            if len(output) >= decomp_size:
                break
            if src_pos >= len(compressed_data):
                break
                
            if control & (1 << i):
                # Literal byte
                output.append(compressed_data[src_pos])
                src_pos += 1
            else:
                # Back reference
                if src_pos + 1 >= len(compressed_data):
                    break
                ref = struct.unpack('<H', compressed_data[src_pos:src_pos+2])[0]
                src_pos += 2
                
                offset = (ref >> 4) + 1
                length = (ref & 0xF) + 3
                
                # Copy from back reference
                if len(output) < offset:
                    # Invalid back reference - corrupted data
                    break
                for j in range(length):
                    if len(output) >= decomp_size:
                        break
                    output.append(output[-offset])
    
    return bytes(output[:decomp_size])

def main():
    if len(sys.argv) != 3:
        print("Usage: python lzss_tool.py <input> <output>")
        sys.exit(1)
    
    try:
        with open(sys.argv[1], 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Error: File {sys.argv[1]} not found")
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied reading {sys.argv[1]}")
        sys.exit(1)
    
    decompressed = decompress_lzss(data)
    
    try:
        with open(sys.argv[2], 'wb') as f:
            f.write(decompressed)
    except PermissionError:
        print(f"Error: Permission denied writing to {sys.argv[2]}")
        sys.exit(1)
    
    print(f"Decompressed {len(data)} -> {len(decompressed)} bytes")

if __name__ == "__main__":
    main()