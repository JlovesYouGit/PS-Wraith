@echo off
title Persistent Device Monitor

echo ====================================================================
echo    ██████╗ ███████╗████████╗██████╗  █████╗ ██╗     ███████╗
echo    ██╔══██╗██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██║     ██╔════╝
echo    ██████╔╝█████╗     ██║   ██████╔╝███████║██║     █████╗  
echo    ██╔═══╝ ██╔══╝     ██║   ██╔══██╗██╔══██║██║     ██╔══╝  
echo    ██║     ███████╗   ██║   ██║  ██║██║  ██║███████╗███████╗
echo    ╚═╝     ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝
echo ====================================================================
echo    PERSISTENT DEVICE MONITORING AND DEACTIVATION SYSTEM
echo ====================================================================
echo    CONTINUOUSLY MONITOR AND PREVENT DEVICE REACTIVATION
echo ====================================================================

echo.
echo Initializing persistent device monitor...
timeout /t 3 /nobreak >nul

echo.
echo This system continuously monitors devices to prevent reactivation.
echo WARNING: This process will maintain permanent device deactivation.
echo The monitoring will continue indefinitely to ensure security.
echo.

python persistent_device_monitor.py

echo.
echo Persistent monitoring sequence completed.
echo.

pause