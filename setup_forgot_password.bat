@echo off
REM ================= FORGOT PASSWORD FEATURE SETUP =================
REM Run this script to install dependencies for the forgot password feature

echo Installing required Python packages...
pip install Flask-Mail python-dotenv

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Dependencies installed successfully!
    echo.
    echo Next steps:
    echo 1. Rename .env.example to .env
    echo 2. Fill in your email credentials in .env
    echo 3. Run the SQL migration in DATABASE_MIGRATIONS.sql
    echo 4. Restart your Flask server
    echo.
    echo For Gmail:
    echo - Enable 2FA: https://myaccount.google.com/
    echo - Generate app password: https://myaccount.google.com/apppasswords
    echo - Use the 16-char password in .env
    echo.
    pause
) else (
    echo ❌ Installation failed! Check your Python/pip setup.
    pause
)
