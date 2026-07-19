#!/usr/bin/env python3
import subprocess
from pathlib import Path

def restore_ipad():
    chargfast_dir = Path("N:/ROMLOADDER/chargfast via usb")
    rom_path = Path("N:/ROMLOADDER/iPad1,1_4.3.3_8J3_Restore.ipsw")
    
    idevicerestore = chargfast_dir / "idevicerestore.exe"
    
    print("Restoring iPad with custom ROM...")
    
    try:
        subprocess.run([
            str(idevicerestore),
            "--custom",
            "--cydia", 
            "--erase",
            "--no-input",
            "-R",
            str(rom_path)
        ], cwd=str(chargfast_dir), check=True)
        
        print("Custom ROM restored successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error restoring: {e}")

if __name__ == "__main__":
    restore_ipad()
