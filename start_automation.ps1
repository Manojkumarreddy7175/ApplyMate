# Scheduled Job Automation Launcher (PowerShell)
# Runs browser automation at scheduled times

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " ApplyMate Scheduled Automation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (Test-Path "applymate-env\Scripts\Activate.ps1") {
    & "applymate-env\Scripts\Activate.ps1"
} elseif (Test-Path ".venv\Scripts\Activate.ps1") {
    & ".venv\Scripts\Activate.ps1"
} else {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run setup.ps1 first" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "ERROR: .env file not found!" -ForegroundColor Red
    Write-Host "Please copy env.example to .env and configure it" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Select mode:" -ForegroundColor Green
Write-Host "1. Start scheduled automation (runs at configured times)"
Write-Host "2. Run automation NOW (one-time)"
Write-Host "3. Test configuration"
Write-Host "4. Exit"
Write-Host ""

$choice = Read-Host "Enter choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Starting scheduled automation..." -ForegroundColor Green
        Write-Host "This will run at configured times (default: 9 AM and 6 PM weekdays)" -ForegroundColor Yellow
        Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
        Write-Host ""
        python scheduled_automation.py
    }
    "2" {
        Write-Host ""
        Write-Host "Running automation NOW..." -ForegroundColor Green
        Write-Host ""
        python scheduled_automation.py now
        Write-Host ""
        Write-Host "Automation complete!" -ForegroundColor Green
        Read-Host "Press Enter to exit"
    }
    "3" {
        Write-Host ""
        Write-Host "Testing configuration..." -ForegroundColor Green
        Write-Host ""
        python scheduled_automation.py test
        Read-Host "Press Enter to exit"
    }
    "4" {
        Write-Host "Exiting..." -ForegroundColor Yellow
        exit 0
    }
    default {
        Write-Host "Invalid choice!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Read-Host "Press Enter to exit"
