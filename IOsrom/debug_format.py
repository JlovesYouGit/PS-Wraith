#!/usr/bin/env python3
import os
import sys

def analyze_file(filepath):
    """Analyze file format"""
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    
    with open(filepath, 'rb') as f:
        data = f.read(64)  # Read first 64 bytes
    
    print(f"\nFile: {filepath}")
    print(f"Size: {os.path.getsize(filepath)} bytes")
    print(f"First 32 bytes (hex): {data[:32].hex()}")
    print(f"First 16 bytes (ascii): {repr(data[:16])}")
    
    # Check for known formats
    if data.startswith(b'IMG4'):
        print("Format: IMG4")
    elif data.startswith(b'Img3'):
        print("Format: IMG3")
    elif data.startswith(b'complzss'):
        print("Format: LZSS compressed")
    elif data.startswith(b'\x89PNG'):
        print("Format: PNG image")
    else:
        print("Format: Unknown")

if __name__ == "__main__":
    # Analyze extracted files
    extract_dir = "workspace/extracted"
    if os.path.exists(extract_dir):
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if any(x in file.lower() for x in ['kernelcache', 'iboot', 'devicetree']):
                    analyze_file(os.path.join(root, file))
    else:
        print("No extracted directory found")