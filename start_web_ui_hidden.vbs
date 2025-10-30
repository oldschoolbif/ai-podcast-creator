Set WshShell = CreateObject("WScript.Shell")
' Change to the script directory
scriptDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = scriptDir

' Run Python in a hidden window
WshShell.Run "python launch_web_gui.py --port 7861", 0, False

' Wait 5 seconds for server to start
WScript.Sleep 5000

' Open browser
WshShell.Run "http://localhost:7861", 1, False

' Show notification
WshShell.Popup "AI Podcast Creator web interface is now running at http://localhost:7861" & vbCrLf & vbCrLf & "To stop the server, run 'stop_web_ui.bat'", 5, "AI Podcast Creator", 64

