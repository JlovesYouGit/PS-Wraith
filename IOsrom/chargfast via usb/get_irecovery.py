#!/usr/bin/env python3
"""
Download irecovery and libusb for Windows
"""
import urllib.request
import json
import sys

def get_latest_release():
    """Get the latest libirecovery release."""
    try:
        # Try multiple repositories
        repos = [
            "libimobiledevice-win32/libirecovery",
            "libimobiledevice/libirecovery"
        ]
        
        for repo in repos:
            try:
                url = f"https://api.github.com/repos/{repo}/releases/latest"
                print(f"Checking {repo}...")
                
                with urllib.request.urlopen(url) as response:
                    data = json.loads(response.read().decode())
                
                print(f"Latest release: {data['tag_name']}")
                
                # Look for Windows assets
                for asset in data['assets']:
                    name = asset['name'].lower()
                    if 'win' in name and ('.zip' in name or '.exe' in name):
                        print(f"Found Windows asset: {asset['name']}")
                        print(f"Download URL: {asset['browser_download_url']}")
                        return asset['browser_download_url']
                
            except Exception as e:
                print(f"Failed to check {repo}: {e}")
                continue
        
        return None
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def download_prebuilt():
    """Download pre-built irecovery."""
    # Known working URLs
    urls = [
        "https://github.com/libimobiledevice-win32/imobiledevice-net/releases/download/v1.3.17/libimobiledevice.1.2.1-r1104-win-x64.zip",
        "https://assets.checkra.in/downloads/windows/cli/x86_64/054faac57d93c724c0f47b5850c7c8ba2c2b5c9b/checkra1n.exe"
    ]
    
    for url in urls:
        try:
            print(f"Trying: {url}")
            filename = url.split('/')[-1]
            urllib.request.urlretrieve(url, filename)
            print(f"Downloaded: {filename}")
            return filename
        except Exception as e:
            print(f"Failed: {e}")
    
    return None

def main():
    """Main function."""
    print("🔧 Getting irecovery for Windows...")
    
    # Try to get latest release
    url = get_latest_release()
    if url:
        try:
            filename = url.split('/')[-1]
            print(f"Downloading {filename}...")
            urllib.request.urlretrieve(url, filename)
            print(f"✅ Downloaded: {filename}")
            return 0
        except Exception as e:
            print(f"Download failed: {e}")
    
    # Try pre-built versions
    print("Trying pre-built versions...")
    if download_prebuilt():
        return 0
    
    print("❌ All download attempts failed")
    print("💡 Manual download required:")
    print("   1. Go to: https://github.com/libimobiledevice/libirecovery/releases")
    print("   2. Download Windows binaries")
    print("   3. Extract irecovery.exe to current directory")
    
    return 1

if __name__ == "__main__":
    sys.exit(main())