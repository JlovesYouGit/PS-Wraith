@echo off
echo PERMANENT SOURCE ELIMINATOR
echo ==========================
echo Metering-based elimination targeting device at source
echo.
timeout /t 2 /nobreak >nul
python permanent_source_eliminator.py
echo.
echo Press any key to exit...
pause >nul