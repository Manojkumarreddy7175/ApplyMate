@echo off
echo ApplyMate Setup Script
echo =====================

echo.
echo 1. Creating virtual environment...
uv venv applymate-env

echo.
echo 2. Activating virtual environment...
call applymate-env\Scripts\activate

echo.
echo 3. Installing dependencies...
uv pip install -r requirements.txt

echo.
echo 4. Setting up configuration files...
if not exist .env (
    copy env.example .env
    echo Created .env file from template
) else (
    echo .env file already exists
)

if not exist personal_info.json (
    copy personal_info.example.json personal_info.json
    echo Created personal_info.json from template
) else (
    echo personal_info.json already exists
)

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Edit .env with your API keys
echo 2. Edit personal_info.json with your information
echo 3. Run: streamlit run app.py
echo.
echo Or run directly: python agent.py
echo.
pause


