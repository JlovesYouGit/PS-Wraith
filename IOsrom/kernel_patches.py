#!/usr/bin/env python3
import struct
import sys

def patch_kernelcache(kernel_path):
    try:
        with open(kernel_path, 'rb') as f:
            data = bytearray(f.read())
    except FileNotFoundError:
        print(f"Error: File {kernel_path} not found")
        return
    except PermissionError:
        print(f"Error: Permission denied accessing {kernel_path}")
        return
    
    # Remove A5 drivers - SGX543 references
    sgx543_refs = [
        b'sgx543',
        b'SGX543',
        b'PowerVR SGX 543MP2'
    ]
    
    for ref in sgx543_refs:
        while ref in data:
            idx = data.find(ref)
            if idx != -1:
                data[idx:idx+len(ref)] = b'\x00' * len(ref)
    
    # Inject A4 GPU driver references
    sgx535_patch = b'PowerVR SGX 535\x00\x00\x00'
    sgx543_target = b'PowerVR SGX 543MP2'
    
    idx = data.find(sgx543_target)
    if idx != -1:
        data[idx:idx+len(sgx543_target)] = sgx535_patch[:len(sgx543_target)]
    
    # Patch memory constraints for A4
    # Change memory size checks from 512MB to 256MB
    mem_patches = [
        (b'\x00\x00\x00\x20', b'\x00\x00\x00\x10'),  # 512MB -> 256MB
        (b'\x00\x00\x20\x00', b'\x00\x00\x10\x00'),  # Alternative endian
    ]
    
    for old, new in mem_patches:
        while old in data:
            idx = data.find(old)
            if idx != -1:
                data[idx:idx+len(old)] = new
    
    try:
        with open(kernel_path + '.patched', 'wb') as f:
            f.write(data)
    except PermissionError:
        print(f"Error: Permission denied writing to {kernel_path}.patched")
        return
    
    print(f"Kernelcache patched: {kernel_path}.patched")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python kernel_patches.py <kernel_path>")
        sys.exit(1)
    patch_kernelcache(sys.argv[1])
