#!/usr/bin/env python3
"""Configuration and constants for iOS9toA4 project"""

# Hardware mappings
HARDWARE_MAPPINGS = {
    'soc_ids': {
        'A5_TO_A4': [
            (b'S5L8940', b'S5L8930'),  # iPad2,1 -> iPad1,1
            (b'S5L8942', b'S5L8930'),  # iPad2,2/3 -> iPad1,1
            (b'\x40\x89', b'\x30\x89'),  # Chip ID bytes
            (b'\x42\x89', b'\x30\x89'),  # Variant chip ID
        ]
    },
    'memory': {
        'A5_TO_A4': [
            (b'\x00\x00\x00\x20', b'\x00\x00\x00\x10'),  # 512MB -> 256MB
            (b'\x20\x00\x00\x00', b'\x10\x00\x00\x00'),  # Alternative endian
        ]
    },
    'gpu': {
        'A5_TO_A4': [
            (b'SGX543MP2', b'SGX535\x00\x00\x00'),
            (b'PowerVR SGX 543MP2', b'PowerVR SGX 535\x00\x00\x00\x00'),
        ]
    },
    'cpu': {
        'A5_TO_A4': [
            (b'cpu,arm-cortex-a9', b'cpu,arm-cortex-a8'),
            (b'Apple A5', b'Apple A4'),
        ]
    }
}

# File patterns
COMPONENT_PATTERNS = {
    'kernelcache': ['kernelcache', 'kernel'],
    'iboot': ['iboot', 'iBoot'],
    'devicetree': ['devicetree', 'DeviceTree'],
    'bootlogo': ['applelogo', 'AppleLogo'],
    'recovery': ['recoverymode', 'RecoveryMode']
}

# Supported devices
DEVICE_MAPPINGS = {
    'source': {
        'iPad2,1': 'iPad 2 Wi-Fi (A5)',
        'iPad2,2': 'iPad 2 Wi-Fi + 3G (A5)',
        'iPad2,3': 'iPad 2 Wi-Fi + 3G (A5)'
    },
    'target': {
        'iPad1,1': 'iPad Wi-Fi (A4)'
    }
}

# ARM instruction constants
ARM_INSTRUCTIONS = {
    'NOP': b'\x00\xF0\x20\xE3',  # ARM NOP instruction
    'BRANCH_PATTERNS': [
        b'\x00\x00\x00\x0A',  # BEQ (branch if equal)
        b'\x00\x00\x00\x1A',  # BNE (branch if not equal)
    ]
}

# Paths and directories
DEFAULT_WORKSPACE = "workspace"
DEFAULT_OUTPUT = "output"

# Logging configuration
LOG_FORMAT = '[%(asctime)s] [%(levelname)s] %(message)s'
LOG_LEVEL = 'INFO'