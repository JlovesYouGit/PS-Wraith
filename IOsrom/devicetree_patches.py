#!/usr/bin/env python3
import struct
import sys

def patch_devicetree(dt_path):
    try:
        with open(dt_path, 'rb') as f:
            data = bytearray(f.read())
    except FileNotFoundError:
        print(f"Error: File {dt_path} not found")
        return
    except PermissionError:
        print(f"Error: Permission denied accessing {dt_path}")
        return
    
    # Fix memory map for A4 (256MB instead of 512MB)
    memory_patches = [
        # DRAM size patches
        (b'\x00\x00\x00\x20\x00\x00\x00\x00', b'\x00\x00\x00\x10\x00\x00\x00\x00'),
        # Memory node size
        (b'\x20\x00\x00\x00', b'\x10\x00\x00\x00'),
    ]
    
    for old, new in memory_patches:
        idx = 0
        while True:
            idx = data.find(old, idx)
            if idx == -1:
                break
            data[idx:idx+len(old)] = new
            idx += len(new)
    
    # GPIO configuration changes for A4
    gpio_patches = [
        # Update GPIO base addresses
        (b'\x00\x00\xE0\xBF', b'\x00\x00\xE0\x3F'),  # GPIO base
        (b'\x00\x10\xE0\xBF', b'\x00\x10\xE0\x3F'),  # GPIO1 base
    ]
    
    for old, new in gpio_patches:
        idx = 0
        while True:
            idx = data.find(old, idx)
            if idx == -1:
                break
            data[idx:idx+len(old)] = new
            idx += len(new)
    
    # CPU identifier change (A5 -> A4)
    cpu_patches = [
        (b'cpu,arm-cortex-a9', b'cpu,arm-cortex-a8'),
        (b'Apple A5', b'Apple A4'),
        (b'S5L8940', b'S5L8930'),  # SoC identifier
    ]
    
    for old, new in cpu_patches:
        idx = 0
        while True:
            idx = data.find(old, idx)
            if idx == -1:
                break
            data[idx:idx+len(old)] = new + b'\x00' * (len(old) - len(new))
            idx += len(old)
    
    try:
        with open(dt_path + '.patched', 'wb') as f:
            f.write(data)
    except PermissionError:
        print(f"Error: Permission denied writing to {dt_path}.patched")
        return
    
    print(f"DeviceTree patched: {dt_path}.patched")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python devicetree_patches.py <devicetree_path>")
        sys.exit(1)
    patch_devicetree(sys.argv[1])