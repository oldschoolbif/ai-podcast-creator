@echo off
REM Stop AI Podcast Creator Web Interface

echo Stopping AI Podcast Creator Web Interface...

REM Kill all Python processes (be careful if you have other Python apps running)
taskkill /F /IM python.exe /T >nul 2>&1

echo.
echo Web server stopped!
echo.
pause

