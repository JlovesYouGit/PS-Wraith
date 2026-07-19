#!/usr/bin/env python3
"""
Build script for creating SpectrumAnalyzer Pro executable.
Uses PyInstaller to create a standalone executable.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def install_pyinstaller():
    """Install PyInstaller if not already installed."""
    try:
        import PyInstaller

        print("✅ PyInstaller already installed")
        return True
    except ImportError:
        print("📦 Installing PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install PyInstaller")
            return False


def create_spec_file():
    """Create PyInstaller spec file."""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Data files to include
datas = [
    ('spectrum_grabber', 'spectrum_grabber'),
    ('spectrum_analysis', 'spectrum_analysis'),
    ('requirements.txt', '.'),
    ('README.md', '.'),
]

# Hidden imports that PyInstaller might miss
hiddenimports = [
    'matplotlib.backends.backend_tkagg',
    'matplotlib.backends.backend_agg',
    'numpy',
    'scipy',
    'tkinter',
    'tkinter.ttk',
    'tkinter.scrolledtext',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'requests',
    'folium',
    'jinja2',
    'urllib3',
    'psutil',
    'xml.etree.ElementTree',
    'json',
    'csv',
    'threading',
    'subprocess',
    'platform',
    'ctypes',
    'mpl_toolkits.mplot3d',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SpectrumAnalyzer-Pro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''

    with open('SpectrumAnalyzer-Pro.spec', 'w') as f:
        f.write(spec_content)

    print("✅ Created PyInstaller spec file")


def build_executable():
    """Build the executable using PyInstaller."""
    print("🔨 Building executable...")

    try:
        # Clean previous builds
        if os.path.exists('build'):
            shutil.rmtree('build')
        if os.path.exists('dist'):
            shutil.rmtree('dist')

        # Run PyInstaller
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", "SpectrumAnalyzer-Pro.spec"]
        subprocess.check_call(cmd)

        print("✅ Executable built successfully!")
        print(f"📁 Executable location: {Path('dist/SpectrumAnalyzer-Pro.exe').absolute()}")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False


def create_installer_script():
    """Create a simple installer script."""
    installer_content = '''@echo off
echo Installing SpectrumAnalyzer Pro...

REM Create installation directory
set INSTALL_DIR=%PROGRAMFILES%\\SpectrumAnalyzer-Pro
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy executable
copy "SpectrumAnalyzer-Pro.exe" "%INSTALL_DIR%\\"

REM Create desktop shortcut
set DESKTOP=%USERPROFILE%\\Desktop
echo [InternetShortcut] > "%DESKTOP%\\SpectrumAnalyzer-Pro.lnk"
echo URL=file:///%INSTALL_DIR%\\SpectrumAnalyzer-Pro.exe >> "%DESKTOP%\\SpectrumAnalyzer-Pro.lnk"

REM Add to PATH (optional)
setx PATH "%PATH%;%INSTALL_DIR%" /M

echo.
echo Installation complete!
echo You can now run SpectrumAnalyzer Pro from:
echo - Desktop shortcut
echo - Command line: SpectrumAnalyzer-Pro
echo - Start menu
echo.
pause
'''

    with open('dist/install.bat', 'w') as f:
        f.write(installer_content)

    print("✅ Created installer script: dist/install.bat")


def main():
    """Main build process."""
    print("🚀 SpectrumAnalyzer Pro Build Script")
    print("=" * 40)

    # Check Python version

    # Install PyInstaller
    if not install_pyinstaller():
        return 1

    # Create spec file
    create_spec_file()

    # Build executable
    if not build_executable():
        return 1

    # Create installer
    create_installer_script()

    print("\n🎉 Build process completed!")
    print("\nNext steps:")
    print("1. Test the executable: dist/SpectrumAnalyzer-Pro.exe")
    print("2. Run installer (as admin): dist/install.bat")
    print("3. Distribute the dist/ folder to users")

    return 0


if __name__ == "__main__":
    sys.exit(main())
