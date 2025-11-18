# Mail Watcher Launcher for PowerShell
# Quick start script for the ApplyMate mail watcher

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " ApplyMate Mail Watcher Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "applymate-env\Scripts\Activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run setup.ps1 first" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
& "applymate-env\Scripts\Activate.ps1"

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "ERROR: .env file not found!" -ForegroundColor Red
    Write-Host "Please copy env.example to .env and configure it" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Select mode:" -ForegroundColor Green
Write-Host "1. Continuous monitoring (runs until stopped)"
Write-Host "2. One-time check (process current emails and exit)"
Write-Host "3. Test configuration"
Write-Host "4. Exit"
Write-Host ""

$choice = Read-Host "Enter choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Starting continuous mail watcher..." -ForegroundColor Green
        Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
        Write-Host ""
        python mail_watcher.py
    }
    "2" {
        Write-Host ""
        Write-Host "Running one-time check..." -ForegroundColor Green
        Write-Host ""
        $env:MAIL_WATCHER_MODE = "once"
        python mail_watcher.py
        Write-Host ""
        Write-Host "One-time check complete!" -ForegroundColor Green
        Read-Host "Press Enter to exit"
    }
    "3" {
        Write-Host ""
        Write-Host "Testing configuration..." -ForegroundColor Green
        Write-Host ""
        python test_mail_watcher.py
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
