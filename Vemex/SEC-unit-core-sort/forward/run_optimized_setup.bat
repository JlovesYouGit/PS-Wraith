@echo off
echo OPTIMIZED NETWORK SETUP
echo ======================
echo Configuring network adapter and router for maximum transmission power
echo.
timeout /t 2 /nobreak >nul
python optimized_network_setup.py
echo.
echo Press any key to exit...
pause >nul