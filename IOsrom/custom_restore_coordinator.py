#!/usr/bin/env python3
"""Custom restore coordinator - prepare device-specific restore"""
import subprocess
import plistlib
import zipfile
from pathlib import Path

def get_device_info():
    """Get device-specific info"""
    chargfast_dir = Path("N:/ROMLOADDER/chargfast via usb")
    irecovery = chargfast_dir / "irecovery.exe"
    
    result = subprocess.run([str(irecovery), "-q"], 
                           capture_output=True, text=True, cwd=str(chargfast_dir))
    
    info = {}
    for line in result.stdout.split('\n'):
        if ':' in line:
            key, val = line.split(':', 1)
            info[key.strip()] = val.strip()
    
    return {
        'ECID': info.get('ECID', '0x0000022da6043df7'),
        'CPID': info.get('CPID', '0x8930'),
        'BDID': info.get('BDID', '0x02'),
        'Model': 'iPad1,1'
    }

def prepare_custom_ipsw(device_info):
    """Prepare IPSW with device-specific values"""
    base_dir = Path("N:/ROMLOADDER")
    ipsw = base_dir / "iPad1,1_4.3.3_8J3_Restore.ipsw"
    custom_ipsw = base_dir / "iPad1,1_Custom_Ready.ipsw"
    work_dir = base_dir / "custom_work"
    
    work_dir.mkdir(exist_ok=True)
    
    print(f"[+] Preparing custom IPSW for ECID: {device_info['ECID']}")
    
    # Extract IPSW
    print("[+] Extracting IPSW...")
    with zipfile.ZipFile(ipsw, 'r') as z:
        z.extractall(work_dir)
    
    # Modify BuildManifest for your device
    manifest_path = work_dir / "BuildManifest.plist"
    if manifest_path.exists():
        print("[+] Customizing BuildManifest...")
        with open(manifest_path, 'rb') as f:
            manifest = plistlib.load(f)
        
        # Set device-specific values
        if 'BuildIdentities' in manifest:
            for identity in manifest['BuildIdentities']:
                if 'Info' in identity:
                    identity['Info']['DeviceClass'] = 'iPad'
                    identity['Info']['MinimumSystemPartition'] = 1024
                
                # Set NAND partition layout for iPad1,1
                if 'Manifest' in identity:
                    # Ensure correct partition addresses
                    if 'LLB' in identity['Manifest']:
                        identity['Manifest']['LLB']['Info'] = {
                            'Path': 'Firmware/all_flash/all_flash.k48ap.production/LLB.k48ap.RELEASE.img3',
                            'Offset': 0
                        }
                    if 'iBoot' in identity['Manifest']:
                        identity['Manifest']['iBoot']['Info'] = {
                            'Path': 'Firmware/all_flash/all_flash.k48ap.production/iBoot.k48ap.RELEASE.img3',
                            'Offset': 1048576  # 0x100000
                        }
        
        # Save modified manifest
        with open(manifest_path, 'wb') as f:
            plistlib.dump(manifest, f)
    
    # Create custom IPSW
    print("[+] Creating custom IPSW...")
    with zipfile.ZipFile(custom_ipsw, 'w', zipfile.ZIP_DEFLATED) as z:
        for file in work_dir.rglob('*'):
            if file.is_file():
                arcname = file.relative_to(work_dir)
                z.write(file, arcname)
    
    print(f"[+] Custom IPSW ready: {custom_ipsw}")
    return custom_ipsw

def flash_custom_ipsw(custom_ipsw, device_info):
    """Flash the prepared IPSW"""
    chargfast_dir = Path("N:/ROMLOADDER/chargfast via usb")
    idevicerestore = chargfast_dir / "idevicerestore.exe"
    
    print(f"[+] Flashing custom IPSW for {device_info['Model']}...")
    
    # Use idevicerestore with custom IPSW
    result = subprocess.run([
        str(idevicerestore),
        "--custom",
        "--erase",
        "--no-input",
        "-i", device_info['ECID'],  # Target specific ECID
        str(custom_ipsw)
    ], cwd=str(chargfast_dir))
    
    return result.returncode == 0

def main():
    """Main restore coordinator"""
    print("CUSTOM RESTORE COORDINATOR")
    print("=" * 30)
    
    # Get device info
    print("[+] Reading device info...")
    device_info = get_device_info()
    print(f"    ECID: {device_info['ECID']}")
    print(f"    Model: {device_info['Model']}")
    
    # Prepare custom IPSW
    custom_ipsw = prepare_custom_ipsw(device_info)
    
    # Flash it
    success = flash_custom_ipsw(custom_ipsw, device_info)
    
    if success:
        print("[+] RESTORE COMPLETE!")
    else:
        print("[-] Restore failed")

if __name__ == "__main__":
    main()
