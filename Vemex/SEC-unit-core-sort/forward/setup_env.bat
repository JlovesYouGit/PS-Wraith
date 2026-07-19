@echo off
echo Setting up Python virtual environment for Threat Elimination System
echo ===============================================================
echo.

echo Creating virtual environment...
python -m venv threat_elimination_env
if %errorlevel% neq 0 (
    echo Failed to create virtual environment
    exit /b %errorlevel%
)

echo.
echo Activating virtual environment...
call threat_elimination_env\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment
    exit /b %errorlevel%
)

echo.
echo Upgrading pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo Failed to upgrade pip
    exit /b %errorlevel%
)

echo.
echo Installing required dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies
    exit /b %errorlevel%
)

echo.
echo Setup complete! Virtual environment is ready.
echo To activate the environment in the future, run:
echo   threat_elimination_env\Scripts\activate.bat
echo.
echo Press any key to exit...
pause >nul