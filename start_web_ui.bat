@echo off
REM Start AI Podcast Creator Web Interface in minimized window

echo Starting AI Podcast Creator Web Interface...
echo.
echo The web server will run in the background.
echo Access at: http://localhost:7861
echo.
echo To stop the server, close this window or press Ctrl+C
echo.

cd /d "%~dp0"
start /min "AI Podcast Creator Web Server" python launch_web_gui.py --port 7861

echo Web server started!
echo Opening browser in 3 seconds...
timeout /t 3 /nobreak >nul

start http://localhost:7861

echo.
echo The web interface is now running at http://localhost:7861
echo This window can be minimized but should not be closed.
pause

