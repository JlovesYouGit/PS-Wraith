#!/usr/bin/env python3
"""
AndroidRoot - Android-native root/boot exploit chain
Equivalent to iOS IOsrom toolset

Tools:
- fastboot_exploit.py: Fastboot mode bootloader exploitation
- android_nand_tool.py: Direct NAND/eMMC/block device access
- boot_image_patcher.py: Android boot.img patching and repacking
- adb_root_chain.py: ADB-based root and privilege escalation
- qualcomm_edl.py: Qualcomm Emergency Download mode
- mediatek_brom.py: MediaTek BootROM mode
- ramdisk_booter.py: Custom ramdisk boot without flashing
- avb_bypass.py: Android Verified Boot bypass
- silicon_burner_android.py: Permanent hardware modification
- android_root_chain.py: Main orchestrator for root chain
"""

__version__ = "1.0.0"
__author__ = "PS-enhance"

from .fastboot_exploit import FastbootExploit
from .android_nand_tool import AndroidNANDTool
from .boot_image_patcher import BootImagePatcher, AndroidBootImage
from .adb_root_chain import ADBRootChain
from .qualcomm_edl import QualcommEDL
from .mediatek_brom import MediaTekBROM
from .ramdisk_booter import AndroidRamdiskBooter
from .avb_bypass import AVBBypass
from .silicon_burner_android import AndroidSiliconBurner
from .android_root_chain import AndroidRootChain

__all__ = [
    "FastbootExploit",
    "AndroidNANDTool",
    "BootImagePatcher",
    "AndroidBootImage",
    "ADBRootChain",
    "QualcommEDL",
    "MediaTekBROM",
    "AndroidRamdiskBooter",
    "AVBBypass",
    "AndroidSiliconBurner",
    "AndroidRootChain",
]
