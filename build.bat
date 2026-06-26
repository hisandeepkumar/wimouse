@echo off
echo Installing dependencies...
pip install -r requirements.txt
echo Building executable...
pyinstaller --onefile --windowed --add-data "templates;templates" --name WirelessTrackpad app.py
echo Build complete. Executable is in dist\WirelessTrackpad.exe
pause
