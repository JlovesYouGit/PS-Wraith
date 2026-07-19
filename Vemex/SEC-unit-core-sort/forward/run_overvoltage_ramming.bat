@echo off
title Overvoltage Pulse Ramming System

echo ====================================================================
echo    ██████╗ ██╗   ██╗ █████╗ ██╗      ██████╗ ██╗   ██╗███████╗
echo    ██╔═══██╗██║   ██║██╔══██╗██║     ██╔═══██╗██║   ██║██╔════╝
echo    ██║   ██║██║   ██║███████║██║     ██║   ██║██║   ██║█████╗  
echo    ██║   ██║╚██╗ ██╔╝██╔══██║██║     ██║   ██║╚██╗ ██╔╝██╔══╝  
echo    ╚██████╔╝ ╚████╔╝ ██║  ██║███████╗╚██████╔╝ ╚████╔╝ ███████╗
echo     ╚═════╝   ╚═══╝  ╚═╝  ╚═╝╚══════╝ ╚═════╝   ╚═══╝  ╚══════╝
echo ====================================================================
echo    OVERVOLTAGE PULSE RAMMING SYSTEM - 250V DESTRUCTIVE ATTACK
echo ====================================================================

echo.
echo Initializing overvoltage pulse ramming system...
timeout /t 5 /nobreak >nul

echo.
echo This system floods the device with destructive 250V pulses.
echo WARNING: This process will permanently damage the target device.
echo This action is IRREVERSIBLE and will cause extensive component failure.
echo.

python overvoltage_ramming_system.py

echo.
echo Overvoltage ramming sequence completed.
echo.

pause