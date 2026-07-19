#!/bin/bash

echo "Starting SpectrumAnalyzer Pro..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.9+ using your package manager"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "  macOS: brew install python3"
    echo "  Or download from: https://python.org"
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "ERROR: Python $required_version or higher is required"
    echo "Current version: $python_version"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

# Check for required system packages on Linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Checking system dependencies..."
    
    # Check for tkinter
    python3 -c "import tkinter" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "WARNING: tkinter not found. Install with:"
        echo "  Ubuntu/Debian: sudo apt install python3-tk"
        echo "  CentOS/RHEL: sudo yum install tkinter"
    fi
    
    # Check for NetworkManager (for WiFi scanning)
    if ! command -v nmcli &> /dev/null; then
        echo "WARNING: NetworkManager not found. WiFi scanning may not work."
        echo "  Install with: sudo apt install network-manager"
    fi
fi

# Run the application
echo
echo "Starting SpectrumAnalyzer Pro GUI..."
echo "Note: You may need to run with sudo for WiFi scanning privileges"
echo

python3 main.py gui

# Check exit status
if [ $? -ne 0 ]; then
    echo
    echo "Application exited with an error."
    echo "Try running with sudo if you encountered permission errors:"
    echo "  sudo ./run.sh"
fi
