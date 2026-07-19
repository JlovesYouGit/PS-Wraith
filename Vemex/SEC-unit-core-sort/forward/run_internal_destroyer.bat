@echo off
title Internal Component Destroyer

echo ======================================================
echo INTERNAL COMPONENT DESTROYER FOR ULTRASONIC DEVICES
echo ======================================================

echo.
echo Initializing destruction system...
timeout /t 2 /nobreak >nul

echo.
echo Starting internal component destruction sequence...
echo.

python internal_component_destroyer.py

echo.
echo Destruction sequence completed.
echo.

pause