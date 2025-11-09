@echo off
REM Mail Watcher Launcher for Windows
REM Quick start script for the ApplyMate mail watcher

echo ========================================
echo  ApplyMate Mail Watcher Launcher
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "applymate-env\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
call applymate-env\Scripts\activate.bat

REM Check if .env exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please copy env.example to .env and configure it
    pause
    exit /b 1
)

echo.
echo Select mode:
echo 1. Continuous monitoring (runs until stopped)
echo 2. One-time check (process current emails and exit)
echo 3. Test configuration
echo 4. Exit
echo.

set /p choice="Enter choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Starting continuous mail watcher...
    echo Press Ctrl+C to stop
    echo.
    python mail_watcher.py
) else if "%choice%"=="2" (
    echo.
    echo Running one-time check...
    echo.
    set MAIL_WATCHER_MODE=once
    python mail_watcher.py
    echo.
    echo One-time check complete!
    pause
) else if "%choice%"=="3" (
    echo.
    echo Testing configuration...
    echo.
    python test_mail_watcher.py
) else if "%choice%"=="4" (
    echo Exiting...
    exit /b 0
) else (
    echo Invalid choice!
    pause
    exit /b 1
)

pause
