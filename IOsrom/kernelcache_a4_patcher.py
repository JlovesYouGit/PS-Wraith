#!/usr/bin/env python3
import struct
import mmap
import os
import sys

class KernelPatcher:
    def __init__(self, kernel_path, output_path=None):
        try:
            self.file = open(kernel_path, 'r+b')
            self.mm = mmap.mmap(self.file.fileno(), 0)
        except FileNotFoundError:
            raise FileNotFoundError(f"Kernel file not found: {kernel_path}")
        except PermissionError:
            raise PermissionError(f"Permission denied accessing: {kernel_path}")
        except OSError as e:
            raise OSError(f"Failed to memory-map file: {e}")
        self.output_path = output_path or f"{os.path.splitext(kernel_path)[0]}.patched"
        try:
            self.output_file = open(self.output_path, 'wb')
        except PermissionError:
            raise PermissionError(f"Permission denied writing to: {self.output_path}")
        self.patches_applied = 0

    def find_and_replace(self, old_bytes, new_bytes):
        if len(old_bytes) != len(new_bytes):
            raise ValueError(f"Replacement length mismatch: {len(old_bytes)} != {len(new_bytes)}")
        pos = 0
        while True:
            pos = self.mm.find(old_bytes, pos)
            if pos == -1:
                break
            self.output_file.write(self.mm[pos-2:pos] + new_bytes)
            self.mm[pos:pos+len(old_bytes)] = new_bytes
            self.patches_applied += 1
            pos += len(new_bytes)

    def patch_soc_identifiers(self):
        # S5L8940X -> S5L8930X
        self.find_and_replace(b's5l8940x', b's5l8930x')
        self.find_and_replace(b'S5L8940X', b'S5L8930X')
        self.find_and_replace(b's5l8942x', b's5l8930x')
        self.find_and_replace(b'S5L8942X', b'S5L8930X')
        
        # Chip ID patches
        self.find_and_replace(b'\x40\x89\x00\x00', b'\x30\x89\x00\x00')  # 8940 -> 8930
        self.find_and_replace(b'\x42\x89\x00\x00', b'\x30\x89\x00\x00')  # 8942 -> 8930

    def patch_gpu_driver(self):
        # SGX543MP2 -> SGX535 (pad to same length)
        self.find_and_replace(b'sgx543mp2', b'sgx535\x00\x00\x00')
        self.find_and_replace(b'SGX543MP2', b'SGX535\x00\x00\x00')
        self.find_and_replace(b'PowerVR SGX 543MP2', b'PowerVR SGX 535\x00\x00\x00')
        
        # GPU register base addresses (A5 -> A4)
        self.find_and_replace(b'\x00\x00\x00\xBF', b'\x00\x00\x00\x3F')  # 0xBF000000 -> 0x3F000000

    def patch_memory_map(self):
        # 512MB -> 256MB patches
        self.find_and_replace(b'\x00\x00\x00\x20', b'\x00\x00\x00\x10')  # 0x20000000 -> 0x10000000
        self.find_and_replace(b'\x20\x00\x00\x00', b'\x10\x00\x00\x00')  # Little endian
        
        # Physical memory size in device tree
        self.find_and_replace(b'\x00\x00\x20\x00\x00\x00\x00\x00', b'\x00\x00\x10\x00\x00\x00\x00\x00')

    def disable_dual_core(self):
        # CPU count: 2 -> 1
        self.find_and_replace(b'cpu-count\x00\x00\x00\x02', b'cpu-count\x00\x00\x00\x01')
        
        # SMP scheduler patches - NOP out secondary CPU init
        # ARM NOP instruction: 0xE320F000
        nop = b'\x00\xF0\x20\xE3'
        
        # Find and NOP secondary CPU boot sequences
        smp_patterns = [
            b'\x01\x00\x50\xE3',  # CMP r0, #1 (CPU ID check)
            b'\x00\x00\x51\xE3',  # CMP r1, #0 (secondary CPU check)
        ]
        
        for pattern in smp_patterns:
            pos = 0
            while True:
                pos = self.mm.find(pattern, pos)
                if pos == -1:
                    break
                # Replace next 4 instructions with NOPs
                for i in range(4):
                    if pos + (i*4) + 4 <= len(self.mm):
                        self.mm[pos + (i*4):pos + (i*4) + 4] = nop
                self.patches_applied += 1
                pos += 4

    def patch_peripheral_addresses(self):
        # A5 -> A4 peripheral base address changes
        peripheral_patches = [
            (b'\x00\x00\xE0\xBF', b'\x00\x00\xE0\x3F'),  # GPIO
            (b'\x00\x10\xE0\xBF', b'\x00\x10\xE0\x3F'),  # GPIO1
            (b'\x00\x20\xE0\xBF', b'\x00\x20\xE0\x3F'),  # I2C
            (b'\x00\x30\xE0\xBF', b'\x00\x30\xE0\x3F'),  # SPI
        ]
        
        for old_addr, new_addr in peripheral_patches:
            self.find_and_replace(old_addr, new_addr)

    def apply_all_patches(self):
        print("[+] Patching SoC identifiers...")
        self.patch_soc_identifiers()
        
        print("[+] Patching GPU driver...")
        self.patch_gpu_driver()
        
        print("[+] Patching memory map...")
        self.patch_memory_map()
        
        print("[+] Disabling dual-core scheduling...")
        self.disable_dual_core()
        
        print("[+] Patching peripheral addresses...")
        self.patch_peripheral_addresses()
        
        self.output_file.write(self.mm)
        print(f"[✅] Applied {self.patches_applied} patches successfully")

    def close(self):
        if hasattr(self, 'mm'):
            self.mm.close()
        if hasattr(self, 'file'):
            self.file.close()
        if hasattr(self, 'output_file'):
            self.output_file.close()

if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python kernelcache_a4_patcher.py <kernelcache_path> [<output_path>]")
        sys.exit(1)
    
    kernel_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) == 3 else None
    try:
        patcher = KernelPatcher(kernel_path, output_path)
        patcher.apply_all_patches()
        patcher.close()
        print(f"[✅] Kernelcache patched for A4 compatibility: {patcher.output_path}")
    except (FileNotFoundError, PermissionError, OSError, ValueError) as e:
        print(f"[❌] Error: {e}")
        sys.exit(1)
