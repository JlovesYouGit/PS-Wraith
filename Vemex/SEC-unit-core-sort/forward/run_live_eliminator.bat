@echo off
echo LIVE ROUTER DATA ELIMINATOR
echo ==========================
echo Using real-time router data for precision targeting
echo of ultrasonic emitters
echo.
timeout /t 2 /nobreak >nul
python live_router_data_eliminator.py
echo.
echo Press any key to exit...
pause >nul