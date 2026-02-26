@echo off
echo ========================================
echo Binocular Vision App - Setup Script
echo ========================================
echo.

echo Step 1: Checking Apache configuration...
echo.

set APACHE_CONF=C:\xampp\apache\conf\httpd.conf

if not exist "%APACHE_CONF%" (
    echo ERROR: Apache config file not found at %APACHE_CONF%
    echo Please check your XAMPP installation path.
    pause
    exit /b 1
)

echo Found Apache config file.
echo.

echo Step 2: Enabling mod_rewrite...
echo.

REM Create backup
copy "%APACHE_CONF%" "%APACHE_CONF%.backup" >nul
echo Created backup: %APACHE_CONF%.backup

REM Enable mod_rewrite
powershell -Command "(gc '%APACHE_CONF%') -replace '#LoadModule rewrite_module', 'LoadModule rewrite_module' | Out-File -encoding ASCII '%APACHE_CONF%'"
echo Enabled mod_rewrite module

REM Enable .htaccess
powershell -Command "(gc '%APACHE_CONF%') -replace 'AllowOverride None', 'AllowOverride All' | Out-File -encoding ASCII '%APACHE_CONF%'"
echo Enabled .htaccess support (AllowOverride All)

echo.
echo Step 3: Restarting Apache...
echo.

REM Stop Apache
net stop Apache2.4 2>nul
if %errorlevel% equ 0 (
    echo Apache stopped successfully
) else (
    echo Apache was not running or could not be stopped
)

REM Start Apache
net start Apache2.4
if %errorlevel% equ 0 (
    echo Apache started successfully
) else (
    echo ERROR: Failed to start Apache
    echo Please start Apache manually from XAMPP Control Panel
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Start Flask AI Server: python ai_server.py
echo 2. Test API: http://localhost/binocularai/test_api.php
echo 3. Run Android app and test
echo.
pause
