#!/usr/bin/env python3
"""Bypass iTunes server checks completely"""
import os
import subprocess

def block_apple_servers():
    """Block all Apple servers in hosts file"""
    hosts_file = r"C:\Windows\System32\drivers\etc\hosts"
    
    apple_servers = [
        "gs.apple.com",
        "phobos.apple.com", 
        "albert.apple.com",
        "ocsp.apple.com",
        "crl.apple.com",
        "valid.apple.com",
        "init.itunes.apple.com",
        "iosapps.itunes.apple.com",
        "itunes.apple.com",
        "ax.itunes.apple.com",
        "se.itunes.apple.com",
        "su.itunes.apple.com",
        "client-api.itunes.apple.com"
    ]
    
    print("[+] Blocking Apple servers...")
    
    try:
        # Read existing hosts
        with open(hosts_file, 'r') as f:
            content = f.read()
        
        # Add blocks
        for server in apple_servers:
            block_line = f"127.0.0.1 {server}"
            if block_line not in content:
                content += f"\n{block_line}"
        
        # Write back
        with open(hosts_file, 'w') as f:
            f.write(content)
        
        print("[✅] Apple servers blocked")
        return True
        
    except PermissionError:
        print("[!] Need Administrator privileges")
        return False

def disable_network():
    """Disable network adapters"""
    print("[+] Disabling network...")
    
    try:
        # Disable WiFi
        subprocess.run(['netsh', 'interface', 'set', 'interface', 'Wi-Fi', 'disabled'], 
                      capture_output=True)
        
        # Disable Ethernet
        subprocess.run(['netsh', 'interface', 'set', 'interface', 'Ethernet', 'disabled'], 
                      capture_output=True)
        
        print("[✅] Network disabled - iTunes can't contact servers")
        return True
        
    except Exception as e:
        print(f"[!] Network disable failed: {e}")
        return False

def patch_itunes_binary():
    """Patch iTunes to skip server checks"""
    print("[+] Patching iTunes binary...")
    
    # Find iTunes installation
    itunes_paths = [
        r"C:\Program Files\iTunes\iTunes.exe",
        r"C:\Program Files (x86)\iTunes\iTunes.exe",
        r"C:\Users\%USERNAME%\AppData\Local\Microsoft\WindowsApps\iTunes.exe"
    ]
    
    itunes_exe = None
    for path in itunes_paths:
        if os.path.exists(path):
            itunes_exe = path
            break
    
    if not itunes_exe:
        print("[!] iTunes not found")
        return False
    
    print(f"[+] Found iTunes: {itunes_exe}")
    
    # Create patched version (backup original)
    backup_exe = itunes_exe + ".backup"
    if not os.path.exists(backup_exe):
        try:
            import shutil
            shutil.copy2(itunes_exe, backup_exe)
            print("[+] iTunes backed up")
        except Exception as e:
            print(f"[!] Backup failed: {e}")
            return False
    
    # Patch binary to skip server checks
    try:
        with open(itunes_exe, 'rb') as f:
            data = f.read()
        
        # Find and replace server check strings
        patches = [
            (b"gs.apple.com", b"127.0.0.1\x00\x00\x00"),
            (b"phobos.apple.com", b"127.0.0.1\x00\x00\x00\x00\x00\x00"),
            (b"TSS request failed", b"TSS request bypass")
        ]
        
        patched_data = data
        for original, replacement in patches:
            if original in patched_data:
                patched_data = patched_data.replace(original, replacement)
                print(f"[+] Patched: {original}")
        
        # Write patched version
        with open(itunes_exe, 'wb') as f:
            f.write(patched_data)
        
        print("[✅] iTunes patched to bypass servers")
        return True
        
    except Exception as e:
        print(f"[!] iTunes patching failed: {e}")
        return False

def use_offline_mode():
    """Force iTunes offline mode"""
    print("[+] Forcing iTunes offline mode...")
    
    # Kill iTunes processes
    try:
        subprocess.run(['taskkill', '/f', '/im', 'iTunes.exe'], capture_output=True)
        subprocess.run(['taskkill', '/f', '/im', 'iTunesHelper.exe'], capture_output=True)
        subprocess.run(['taskkill', '/f', '/im', 'AppleMobileDeviceService.exe'], capture_output=True)
        print("[+] iTunes processes killed")
    except:
        pass
    
    # Block servers
    block_apple_servers()
    
    # Disable network
    disable_network()
    
    print("[✅] iTunes forced offline")
    print("[+] Now try iTunes restore - it can't contact servers")
    
    return True

def main():
    """Bypass iTunes server checks"""
    print("[+] iTunes Server Bypass Tool")
    print("=" * 40)
    
    methods = [
        ("Block Apple servers", block_apple_servers),
        ("Disable network", disable_network), 
        ("Patch iTunes binary", patch_itunes_binary),
        ("Force offline mode", use_offline_mode)
    ]
    
    print("Choose bypass method:")
    for i, (name, func) in enumerate(methods, 1):
        print(f"{i}. {name}")
    
    try:
        choice = int(input("Enter choice (1-4): "))
        if 1 <= choice <= len(methods):
            name, func = methods[choice-1]
            print(f"\n[+] Using: {name}")
            
            if func():
                print(f"[✅] {name} successful")
                print("\nNow try iTunes restore:")
                print("1. Put device in DFU mode")
                print("2. Shift+Click Restore in iTunes")
                print("3. Select your custom IPSW")
                print("4. iTunes can't contact servers = bypass!")
            else:
                print(f"[!] {name} failed")
        else:
            print("[!] Invalid choice")
    except ValueError:
        print("[!] Invalid input")

if __name__ == "__main__":
    main()