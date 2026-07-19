#!/usr/bin/env python3
"""Manual complete restore - do what idevicerestore does without limera1n"""
import subprocess
import time
import zipfile
from pathlib import Path

def manual_restore():
    """Manually perform complete restore"""
    chargfast_dir = Path("N:/ROMLOADDER/chargfast via usb")
    irecovery = chargfast_dir / "irecovery.exe"
    ipsw = Path("N:/ROMLOADDER/iPad1,1_4.3.3_8J3_Restore.ipsw")
    
    print("MANUAL COMPLETE RESTORE")
    print("=" * 25)
    
    # Extract IPSW
    work_dir = chargfast_dir / "manual_restore"
    work_dir.mkdir(exist_ok=True)
    
    print("[+] Extracting IPSW...")
    with zipfile.ZipFile(ipsw, 'r') as z:
        z.extractall(work_dir)
    
    # Step 1: Load iBSS/iBEC (replaces limera1n)
    print("[+] Loading iBSS...")
    subprocess.run([str(irecovery), "-f", str(work_dir / "Firmware/dfu/iBSS.k48ap.RELEASE.dfu")], cwd=str(chargfast_dir))
    subprocess.run([str(irecovery), "-c", "go"], cwd=str(chargfast_dir))
    time.sleep(2)
    
    print("[+] Loading iBEC...")
    subprocess.run([str(irecovery), "-f", str(work_dir / "Firmware/dfu/iBEC.k48ap.RELEASE.dfu")], cwd=str(chargfast_dir))
    subprocess.run([str(irecovery), "-c", "go"], cwd=str(chargfast_dir))
    time.sleep(2)
    
    # Step 2: Load restore ramdisk
    print("[+] Loading restore ramdisk...")
    ramdisk = work_dir / "038-1437-004.dmg"
    subprocess.run([str(irecovery), "-f", str(ramdisk)], cwd=str(chargfast_dir))
    subprocess.run([str(irecovery), "-c", "ramdisk"], cwd=str(chargfast_dir))
    
    # Step 3: Load devicetree
    print("[+] Loading devicetree...")
    devicetree = work_dir / "Firmware/all_flash/all_flash.k48ap.production/DeviceTree.k48ap.img3"
    subprocess.run([str(irecovery), "-f", str(devicetree)], cwd=str(chargfast_dir))
    subprocess.run([str(irecovery), "-c", "devicetree"], cwd=str(chargfast_dir))
    
    # Step 4: Load kernel
    print("[+] Loading kernel...")
    kernel = work_dir / "kernelcache.release.k48"
    subprocess.run([str(irecovery), "-f", str(kernel)], cwd=str(chargfast_dir))
    
    # Step 5: Boot to ramdisk
    print("[+] Booting to restore ramdisk...")
    subprocess.run([str(irecovery), "-c", "bootx"], cwd=str(chargfast_dir))
    
    print("[+] Waiting for ramdisk boot (60 seconds)...")
    time.sleep(60)
    
    # Step 6: Device should now be in restore mode with ASR running
    # Use idevicerestore to communicate with ASR
    print("[+] Communicating with ASR...")
    
    idevicerestore = chargfast_dir / "idevicerestore.exe"
    
    # Run idevicerestore but it should skip limera1n since we're already in ramdisk
    result = subprocess.run([
        str(idevicerestore),
        "--erase",
        str(ipsw)
    ], cwd=str(chargfast_dir), timeout=600)
    
    if result.returncode == 0:
        print("[+] RESTORE COMPLETE!")
        return True
    else:
        print("[-] ASR communication failed")
        return False

if __name__ == "__main__":
    manual_restore()
