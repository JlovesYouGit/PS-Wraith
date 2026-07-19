#!/usr/bin/env python
import subprocess
import time

def direct_irecovery_fix():
    """Direct irecovery fix with retry logic."""
    for i in range(50):  # 50 attempts
        try:
            print(f"Attempt {i+1}/50...")
            result = subprocess.run([
                "irecovery.exe", "-c", "setenv auto-boot true; saveenv; reboot"
            ], capture_output=True, text=True, timeout=2)
            
            if result.returncode == 0:
                print("✅ SUCCESS! Device fixed.")
                return True
            
            time.sleep(0.1)  # Quick retry
            
        except subprocess.TimeoutExpired:
            time.sleep(0.1)
        except:
            time.sleep(0.1)
    
    print("❌ Failed after 50 attempts")
    return False

if __name__ == "__main__":
    direct_irecovery_fix()