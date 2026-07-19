#!/usr/bin/env python3
import struct
import sys

def patch_iboot(iboot_path):
    try:
        with open(iboot_path, 'rb') as f:
            data = bytearray(f.read())
    except FileNotFoundError:
        print(f"Error: File {iboot_path} not found")
        return
    except PermissionError:
        print(f"Error: Permission denied accessing {iboot_path}")
        return
    
    # Bypass A5 hardware checks
    # NOP out conditional branches that check for A5
    nop_arm = b'\x00\xF0\x20\xE3'  # ARM NOP instruction
    
    # Common A5 check patterns to bypass
    a5_checks = [
        b'\x40\x89\x5C\x8E',  # A5 chip ID check
        b'\x42\x89\x5C\x8E',  # A5 variant check
    ]
    
    # Replace conditional branches with NOPs
    branch_patterns = [
        b'\x00\x00\x00\x0A',  # BEQ (branch if equal)
        b'\x00\x00\x00\x1A',  # BNE (branch if not equal)
    ]
    
    for pattern in branch_patterns:
        idx = 0
        while True:
            idx = data.find(pattern, idx)
            if idx == -1:
                break
            # Check if this might be an A5 hardware check
            context = data[max(0, idx-20):idx+20]
            if any(check in context for check in a5_checks):
                data[idx:idx+4] = nop_arm
            idx += 4
    
    # Patch hardware ID checks
    hw_id_patches = [
        # Change A5 hardware IDs to A4
        (b'\x40\x89', b'\x30\x89'),  # S5L8940 -> S5L8930
        (b'\x42\x89', b'\x30\x89'),  # S5L8942 -> S5L8930
    ]
    
    for old, new in hw_id_patches:
        idx = 0
        while True:
            idx = data.find(old, idx)
            if idx == -1:
                break
            data[idx:idx+len(old)] = new
            idx += len(new)
    
    # Memory size validation bypass
    mem_checks = [
        (b'\x00\x00\x00\x20', b'\x00\x00\x00\x10'),  # 512MB -> 256MB
        (b'\x20\x00\x00\x00', b'\x10\x00\x00\x00'),  # Alternative endian
    ]
    
    for old, new in mem_checks:
        idx = 0
        while True:
            idx = data.find(old, idx)
            if idx == -1:
                break
            data[idx:idx+len(old)] = new
            idx += len(new)
    
    try:
        with open(iboot_path + '.patched', 'wb') as f:
            f.write(data)
    except PermissionError:
        print(f"Error: Permission denied writing to {iboot_path}.patched")
        return
    
    print(f"iBoot patched: {iboot_path}.patched")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python iboot_patches.py <iboot_path>")
        sys.exit(1)
    patch_iboot(sys.argv[1])