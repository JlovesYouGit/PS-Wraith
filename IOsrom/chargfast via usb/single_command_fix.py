#!/usr/bin/env python
import subprocess
import time

def single_command_fix():
    """Try to execute all commands in one go."""
    combined_cmd = "setenv auto-boot true; saveenv; reboot"
    
    for attempt in range(20):
        try:
            print(f"Attempt {attempt+1}: Executing combined command...")
            result = subprocess.run([
                "irecovery.exe", "-c", combined_cmd
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                print("✅ SUCCESS - Device should reboot normally")
                return True
            else:
                print(f"❌ Failed: {result.stderr}")
                time.sleep(0.2)
                
        except subprocess.TimeoutExpired:
            print("⏱️ Timeout, retrying...")
            time.sleep(0.2)
        except Exception as e:
            print(f"🔄 Error: {e}, retrying...")
            time.sleep(0.2)
    
    print("❌ Failed after 20 attempts")
    return False

if __name__ == "__main__":
    single_command_fix()