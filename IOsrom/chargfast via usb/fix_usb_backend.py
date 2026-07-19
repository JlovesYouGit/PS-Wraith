#!/usr/bin/env python
import subprocess
import sys

def fix_usb_power_management():
    """Disable USB selective suspend causing disconnects."""
    cmd = '''
    powercfg /setacvalueindex scheme_current 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0
    powercfg /setdcvalueindex scheme_current 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0
    powercfg /setactive scheme_current
    
    Get-WmiObject -Class Win32_USBHub | ForEach-Object {
        $deviceID = $_.DeviceID
        $keyPath = "HKLM:\\SYSTEM\\CurrentControlSet\\Enum\\$deviceID\\Device Parameters"
        if (Test-Path $keyPath) {
            Set-ItemProperty -Path $keyPath -Name "SelectiveSuspendEnabled" -Value 0 -Force -ErrorAction SilentlyContinue
        }
    }
    '''
    subprocess.run(["powershell", "-Command", cmd], shell=True)

def fix_apple_drivers():
    """Reset Apple device drivers."""
    cmd = '''
    Stop-Service -Name "Apple Mobile Device Service" -Force -ErrorAction SilentlyContinue
    
    Get-PnpDevice | Where-Object {$_.FriendlyName -like "*Apple*" -or $_.InstanceId -like "*VID_05AC*"} | ForEach-Object {
        Disable-PnpDevice -InstanceId $_.InstanceId -Confirm:$false -ErrorAction SilentlyContinue
        Start-Sleep 1
        Enable-PnpDevice -InstanceId $_.InstanceId -Confirm:$false -ErrorAction SilentlyContinue
    }
    
    Start-Service -Name "Apple Mobile Device Service" -ErrorAction SilentlyContinue
    '''
    subprocess.run(["powershell", "-Command", cmd], shell=True)

if __name__ == "__main__":
    print("🔧 Fixing USB backend...")
    fix_usb_power_management()
    fix_apple_drivers()
    print("✅ USB fixes applied - reconnect device")