# ApplyMate Setup Script (PowerShell)
Write-Host "ApplyMate Setup Script" -ForegroundColor Green
Write-Host "=====================" -ForegroundColor Green

Write-Host ""
Write-Host "1. Creating virtual environment..." -ForegroundColor Yellow
uv venv applymate-env

Write-Host ""
Write-Host "2. Activating virtual environment..." -ForegroundColor Yellow
& "applymate-env\Scripts\Activate.ps1"

Write-Host ""
Write-Host "3. Installing dependencies..." -ForegroundColor Yellow
uv pip install -r requirements.txt

Write-Host ""
Write-Host "4. Setting up configuration files..." -ForegroundColor Yellow
if (!(Test-Path ".env")) {
    Copy-Item "env.example" ".env"
    Write-Host "Created .env file from template" -ForegroundColor Green
} else {
    Write-Host ".env file already exists" -ForegroundColor Cyan
}

if (!(Test-Path "personal_info.json")) {
    Copy-Item "personal_info.example.json" "personal_info.json"
    Write-Host "Created personal_info.json from template" -ForegroundColor Green
} else {
    Write-Host "personal_info.json already exists" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env with your API keys" -ForegroundColor White
Write-Host "2. Edit personal_info.json with your information" -ForegroundColor White
Write-Host "3. Run: streamlit run app.py" -ForegroundColor White
Write-Host ""
Write-Host "Or run directly: python agent.py" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to continue"


