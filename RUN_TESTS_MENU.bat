@echo off
REM Quick launcher for the testing menu
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File .\test_menu.ps1
pause


