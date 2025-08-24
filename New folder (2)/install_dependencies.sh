#!/bin/bash

echo "Installing Python Dependencies for Web Scraper..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.7+ first:"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "  macOS: brew install python3"
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.7"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "ERROR: Python $python_version is installed, but $required_version+ is required"
    exit 1
fi

echo "✓ Python $python_version detected"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 is not installed"
    echo "Please install pip3 first"
    exit 1
fi

echo "✓ pip3 detected"
echo

echo "Installing required packages..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo
    echo "✅ All dependencies installed successfully!"
    echo
    echo "You can now:"
    echo "1. Test installation: python3 test_installation.py"
    echo "2. Run demo: python3 demo.py"
    echo "3. Start scraping: python3 main.py --help"
    echo
    echo "To make scripts executable:"
    echo "  chmod +x *.sh"
else
    echo
    echo "❌ Some dependencies failed to install"
    echo "Check the error messages above"
    exit 1
fi
