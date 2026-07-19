#!/usr/bin/env python3
"""MCP Recovery Tool - Get control then fix NAND"""
import subprocess
import time
from pathlib import Path

def get_pwned_control():
    """Get pwned iBEC control first"""
    base_dir = Path("N:/ROMLOADDER")
    chargfast_dir = base_dir / "chargfast via usb"
    irecovery = chargfast_dir / "irecovery.exe"
    
    print("[MCP] Getting pwned control...")
    
    try:
        # Upload iBSS
        subprocess.run([str(irecovery), "-f", "extracted/Firmware/dfu/iBSS.k48ap.RELEASE.dfu"], 
                      cwd=str(chargfast_dir), timeout=10)
        subprocess.run([str(irecovery), "-c", "go"], cwd=str(chargfast_dir))
        time.sleep(2)
        
        # Upload iBEC
        subprocess.run([str(irecovery), "-f", "extracted/Firmware/dfu/iBEC.k48ap.RELEASE.dfu"], 
                      cwd=str(chargfast_dir), timeout=10)
        subprocess.run([str(irecovery), "-c", "go"], cwd=str(chargfast_dir))
        time.sleep(2)
        
        # Test control
        result = subprocess.run([str(irecovery), "-q"], 
                               capture_output=True, text=True, timeout=5, cwd=str(chargfast_dir))
        
        if result.returncode == 0:
            print("[MCP] ✅ Pwned control achieved")
            return True
        else:
            print("[MCP] ❌ Control failed")
            return False
            
    except Exception as e:
        print(f"[MCP] ❌ Control error: {e}")
        return False

def mcp_direct_nand_fix():
    """Direct NAND fix with MCP control"""
    base_dir = Path("N:/ROMLOADDER")
    chargfast_dir = base_dir / "chargfast via usb"
    irecovery = chargfast_dir / "irecovery.exe"
    
    print("[MCP] Direct NAND fix starting...")
    
    # Get control first
    if not get_pwned_control():
        return False
    
    # Direct NAND commands
    commands = [
        # Unlock NAND
        "mw 0x38100000 0x00000001",
        "mw 0x38100004 0x00000000", 
        "mw 0x38100008 0xFFFFFFFF",
        
        # Open NAND
        "nand open",
        "nand part system",
        "nand erase 0 0x2000000",
    ]
    
    for cmd in commands:
        print(f"[MCP] {cmd}")
        try:
            result = subprocess.run([str(irecovery), "-c", cmd], 
                                   capture_output=True, text=True, timeout=10, cwd=str(chargfast_dir))
            if result.returncode != 0:
                print(f"[MCP] ⚠️  {cmd} failed: {result.stderr}")
        except Exception as e:
            print(f"[MCP] ❌ {cmd} error: {e}")
    
    # Flash components
    components = [
        ("extracted/Firmware/all_flash/all_flash.k48ap.production/LLB.k48ap.RELEASE.img3", 0x0),
        ("extracted/Firmware/all_flash/all_flash.k48ap.production/iBoot.k48ap.RELEASE.img3", 0x100000),
        ("extracted/kernelcache.release.k48", 0x400000),
        ("038-1421-004.dmg", 0x800000)
    ]
    
    for comp, addr in components:
        comp_path = chargfast_dir / comp
        if comp_path.exists():
            print(f"[MCP] Flashing {comp_path.name}")
            try:
                # Upload
                subprocess.run([str(irecovery), "-f", str(comp_path)], 
                              cwd=str(chargfast_dir), timeout=30)
                
                # Write to NAND
                subprocess.run([str(irecovery), "-c", f"nand write 0x{addr:x}"], 
                              cwd=str(chargfast_dir), timeout=30)
                
                print(f"[MCP] ✅ {comp_path.name} flashed")
                
            except Exception as e:
                print(f"[MCP] ❌ {comp_path.name} failed: {e}")
    
    # Final commands
    final_cmds = [
        "nand close",
        "setenv auto-boot true",
        "saveenv",
        "reset"
    ]
    
    for cmd in final_cmds:
        print(f"[MCP] {cmd}")
        try:
            subprocess.run([str(irecovery), "-c", cmd], cwd=str(chargfast_dir), timeout=10)
        except:
            pass
    
    print("[MCP] 🎉 Direct NAND fix complete!")
    return True

if __name__ == "__main__":
    print("🔧 MCP RECOVERY TOOL")
    print("Get control then fix NAND")
    print()
    
    success = mcp_direct_nand_fix()
    
    if success:
        print("\n🎉 MCP SUCCESS!")
        print("NAND should be fixed and device booting")
    else:
        print("\n❌ MCP FAILED!")
        print("Could not get device control")