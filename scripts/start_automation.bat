@echo off
REM Scheduled Job Automation Launcher
REM Runs browser automation at scheduled times

echo ========================================
echo  ApplyMate Scheduled Automation
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "applymate-env\Scripts\activate.bat" (
    if exist ".venv\Scripts\activate.bat" (
        call .venv\Scripts\activate.bat
    ) else (
        echo ERROR: Virtual environment not found!
        echo Please run setup.bat first
        pause
        exit /b 1
    )
) else (
    call applymate-env\Scripts\activate.bat
)

REM Check if .env exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please copy env.example to .env and configure it
    pause
    exit /b 1
)

echo.
echo Select mode:
echo 1. Start scheduled automation (runs at configured times)
echo 2. Run automation NOW (one-time)
echo 3. Test configuration
echo 4. Exit
echo.

set /p choice="Enter choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Starting scheduled automation...
    echo This will run at configured times (default: 9 AM and 6 PM weekdays)
    echo Press Ctrl+C to stop
    echo.
    python scheduled_automation.py
) else if "%choice%"=="2" (
    echo.
    echo Running automation NOW...
    echo.
    python scheduled_automation.py now
    echo.
    echo Automation complete!
    pause
) else if "%choice%"=="3" (
    echo.
    echo Testing configuration...
    echo.
    python scheduled_automation.py test
    pause
) else if "%choice%"=="4" (
    echo Exiting...
    exit /b 0
) else (
    echo Invalid choice!
    pause
    exit /b 1
)

pause
