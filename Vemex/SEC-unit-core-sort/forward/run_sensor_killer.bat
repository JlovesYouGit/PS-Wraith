@echo off
title Proximity Sensor Killer

echo ============================================================
echo PROXIMITY SENSOR KILLER FOR ULTRASONIC DEVICES
echo ============================================================
echo PERMANENTLY DISABLING PROXIMITY DETECTION CAPABILITIES
echo ============================================================

echo.
echo Initializing proximity sensor killer...
timeout /t 3 /nobreak >nul

echo.
echo Starting sensor destruction sequence...
echo.

python proximity_sensor_killer.py

echo.
echo Proximity sensor killing sequence completed.
echo.

pause