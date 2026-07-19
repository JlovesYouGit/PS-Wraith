#!/usr/bin/env python
import subprocess
import time
import sys

def rapid_fix():
    """Fix auto-boot with retry logic for unstable connections."""
    commands = [
        "setenv auto-boot true",
        "saveenv", 
        "reboot"
    ]
    
    for cmd in commands:
        for attempt in range(10):  # 10 attempts per command
            try:
                print(f"Attempt {attempt+1}: {cmd}")
                result = subprocess.run([
                    "irecovery.exe", "-c", cmd
                ], capture_output=True, text=True, timeout=3)
                
                if result.returncode == 0:
                    print(f"✅ {cmd} - SUCCESS")
                    break
                else:
                    print(f"❌ {cmd} - FAILED, retrying...")
                    time.sleep(0.5)
                    
            except subprocess.TimeoutExpired:
                print(f"⏱️ {cmd} - TIMEOUT, retrying...")
                time.sleep(0.5)
            except Exception as e:
                print(f"🔄 {cmd} - ERROR: {e}, retrying...")
                time.sleep(0.5)
        else:
            print(f"❌ {cmd} - FAILED after 10 attempts")
            return False
    
    print("✅ All commands completed!")
    return True

if __name__ == "__main__":
    print("🔄 Rapid Auto-Boot Fixer (handles unstable connections)")
    rapid_fix()