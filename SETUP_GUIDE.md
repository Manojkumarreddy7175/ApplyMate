# ApplyMate - Automated Job Application Agent

## 🚨 CRITICAL SECURITY ISSUES FIXED

### Issues Found:
1. **Hardcoded personal info** in agent.py (John Doe, john@example.com)
2. **Missing environment validation**
3. **Inconsistent configuration files**
4. **No input validation**

## 🛠️ Setup Guide

### Prerequisites
- Python 3.8+
- uv package manager
- Required API keys (see .env.example)

### 1. Install uv (if not already installed)
```bash
# Windows
pip install uv

# Or using pipx
pipx install uv
```

### 2. Create Virtual Environment
```bash
# Create uv environment
uv venv applymate-env

# Activate environment
# Windows
applymate-env\Scripts\activate
# Linux/Mac
source applymate-env/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

### 3. Environment Setup
```bash
# Copy environment template
copy .env.example .env

# Edit .env with your actual credentials
notepad .env
```

### 4. Required API Keys
You need these API keys:
- `GOOGLE_API_KEY` - For Gemini AI
- `FIRECRAWL_API_KEY` - For web scraping
- `BROWSERBASE_API_KEY` - For browser automation
- `BROWSERBASE_PROJECT_ID` - BrowserBase project ID
- `EMAIL_USER` - Your email for notifications
- `EMAIL_PASS` - Email app password (not regular password)

### 5. Personal Information Setup
```bash
# Copy personal info template
copy personal_info.example.json personal_info.json

# Edit with your actual information
notepad personal_info.json
```

### 6. Run the Agent

#### Option A: Streamlit Dashboard (Recommended)
```bash
streamlit run app.py
```

#### Option B: Direct Agent Run
```bash
python agent.py
```

#### Option C: Scheduled Runs
```bash
python main.py
```

## 🔧 Configuration Files

### preferences.json
```json
{
  "title": "Software Engineer",
  "location": "Remote",
  "skills": ["Python", "AI", "Machine Learning"],
  "min_salary": 100000
}
```

### personal_info.json (NEW - for security)
```json
{
  "name": "Your Full Name",
  "email": "your.email@example.com",
  "phone": "+1-xxx-xxx-xxxx",
  "linkedin": "https://linkedin.com/in/yourprofile"
}
```

## 🚀 Quick Start Commands

```bash
# 1. Setup
uv venv applymate-env
applymate-env\Scripts\activate
uv pip install -r requirements.txt

# 2. Configure
copy .env.example .env
copy personal_info.example.json personal_info.json
# Edit both files with your information

# 3. Run
streamlit run app.py
```

## 📋 Troubleshooting

### Common Issues:
1. **Missing API keys** - Check .env file
2. **Resume not found** - Upload resume via Streamlit dashboard
3. **Email not sending** - Use app password, not regular password
4. **MCP tools failing** - Check API keys and internet connection

### Logs:
- Check console output for detailed error messages
- Agent logs are printed to console
- CSV results saved to `jobs_dashboard.csv`

## 🔒 Security Notes

- Never commit .env or personal_info.json to git
- Use app passwords for email, not regular passwords
- Keep API keys secure and rotate regularly
- Review job applications before submitting


