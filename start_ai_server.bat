@echo off
echo ============================================================
echo Starting Binocular Vision AI Server (Flask)
echo ============================================================
echo.
echo This server must run alongside XAMPP for AI analysis to work.
echo.
echo Press Ctrl+C to stop the server when done.
echo ============================================================
echo.

cd /d c:\xampp\htdocs\binocularai
python ai_server.py

pause
