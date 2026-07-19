import os
import sys
import json
import time
import subprocess
from pathlib import Path

def disable_acoustic_detection():
    """
    Disable the acoustic fluctuation detection system.
    """
    print("Disabling Acoustic Fluctuation Detection System...")
    print("=" * 50)
    
    # 1. Check if the acoustic detector is running
    print("1. Checking for running acoustic detection processes...")
    try:
        # Kill any running Python processes that might be the acoustic detector
        subprocess.run(["taskkill", "/f", "/im", "python.exe", "/fi", "WINDOWTITLE eq acoustic*"], 
                      capture_output=True, timeout=5)
        print("   - Terminated acoustic detection processes")
    except Exception as e:
        print(f"   - Error terminating processes: {e}")
    
    # 2. Rename or disable the main acoustic detection script
    print("2. Disabling acoustic detection scripts...")
    acoustic_script = Path("n:/forward/acoustic_fluctuation_detector.py")
    if acoustic_script.exists():
        try:
            # Rename the file to disable it
            disabled_name = acoustic_script.with_name("acoustic_fluctuation_detector_disabled.py")
            acoustic_script.rename(disabled_name)
            print("   - Disabled acoustic_fluctuation_detector.py")
        except Exception as e:
            print(f"   - Error disabling acoustic script: {e}")
    
    # 3. Remove the batch file
    print("3. Removing acoustic detection batch files...")
    batch_file = Path("n:/forward/run_acoustic_detector.bat")
    if batch_file.exists():
        try:
            batch_file.unlink()
            print("   - Removed run_acoustic_detector.bat")
        except Exception as e:
            print(f"   - Error removing batch file: {e}")
    
    # 4. Clean up any result files
    print("4. Cleaning up result files...")
    result_files = [
        Path("n:/forward/acoustic_detection_results.json"),
        Path("n:/forward/short_acoustic_detector.py")
    ]
    
    for result_file in result_files:
        if result_file.exists():
            try:
                result_file.unlink()
                print(f"   - Removed {result_file.name}")
            except Exception as e:
                print(f"   - Error removing {result_file.name}: {e}")
    
    # 5. Update README to remove references
    print("5. Updating documentation...")
    readme_file = Path("n:/forward/README.md")
    if readme_file.exists():
        try:
            with open(readme_file, 'r') as f:
                content = f.read()
            
            # Remove acoustic detection sections
            lines = content.split('\n')
            new_lines = []
            skip_acoustic = False
            
            for line in lines:
                if "Acoustic Fluctuation Detector" in line and "GHz Band Device Detector" not in line:
                    skip_acoustic = True
                elif "## Files Included" in line:
                    skip_acoustic = False
                    new_lines.append(line)
                elif "acoustic_fluctuation_detector.py" in line:
                    continue  # Skip this line
                elif "run_acoustic_detector.bat" in line:
                    continue  # Skip this line
                elif skip_acoustic and line.startswith("## ") and "Acoustic" not in line:
                    skip_acoustic = False
                    new_lines.append(line)
                elif not skip_acoustic:
                    new_lines.append(line)
            
            with open(readme_file, 'w') as f:
                f.write('\n'.join(new_lines))
            
            print("   - Updated README.md")
        except Exception as e:
            print(f"   - Error updating README: {e}")
    
    print("\n" + "=" * 50)
    print("Acoustic detection system has been disabled.")
    print("The 'strong and low band' sound should no longer be generated.")
    print("=" * 50)

def restore_acoustic_detection():
    """
    Restore the acoustic fluctuation detection system.
    """
    print("Restoring Acoustic Fluctuation Detection System...")
    print("=" * 50)
    
    # Rename the disabled script back
    disabled_script = Path("n:/forward/acoustic_fluctuation_detector_disabled.py")
    if disabled_script.exists():
        try:
            original_name = disabled_script.with_name("acoustic_fluctuation_detector.py")
            disabled_script.rename(original_name)
            print("   - Restored acoustic_fluctuation_detector.py")
        except Exception as e:
            print(f"   - Error restoring acoustic script: {e}")
    
    print("\nTo fully restore the system, you would need to recreate:")
    print("   - run_acoustic_detector.bat")
    print("   - Update README.md with acoustic detection information")
    print("=" * 50)

def main():
    """
    Main function to disable or restore the acoustic detection system.
    """
    print("Acoustic Detection System Control")
    print("=" * 35)
    print("This script will disable the acoustic fluctuation detection system")
    print("that may be generating the 'dog whistle' sound you're hearing.")
    print()
    
    choice = input("Enter 'disable' to disable the system or 'restore' to restore it: ").strip().lower()
    
    if choice == 'disable':
        disable_acoustic_detection()
    elif choice == 'restore':
        restore_acoustic_detection()
    else:
        print("Invalid choice. Please run the script again and enter 'disable' or 'restore'.")

if __name__ == "__main__":
    main()