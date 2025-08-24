@echo off
echo Installing Python Dependencies for Web Scraper...
echo.

echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

echo.
echo Installing required packages...
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo.
    echo ✅ All dependencies installed successfully!
    echo.
    echo You can now:
    echo 1. Test installation: python test_installation.py
    echo 2. Run demo: python demo.py
    echo 3. Start scraping: python main.py --help
) else (
    echo.
    echo ❌ Some dependencies failed to install
    echo Check the error messages above
)

echo.
pause
