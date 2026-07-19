
# Manual libusb Installation for Windows

## Method 1: Download Pre-built DLL
1. Visit: https://github.com/libusb/libusb/releases/latest
2. Download: libusb-1.0.27-binaries.7z
3. Extract the archive
4. Copy: MS64/dll/libusb-1.0.dll to your project directory

## Method 2: Use Package Manager
```powershell
# Install scoop if not already installed
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex

# Add buckets and install
scoop bucket add extras
scoop install libusb
```

## Method 3: System Installation
1. Download libusb from official site
2. Install to system PATH
3. Restart terminal

## Test Installation
Run: python flip_minimal_real.py
