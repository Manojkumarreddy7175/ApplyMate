# 🤖 ApplyMate

**AI-Powered Job Application Automation System** with intelligent job matching, scheduled browser automation, and multi-platform support.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 🎯 **Intelligent Job Matching** - AI-powered resume parsing and job relevance scoring
- ⏰ **Scheduled Automation** - Automatic job search and application at configured times
- 🌐 **Multi-Platform Support** - LinkedIn, Indeed, Naukri, Glassdoor, and more
- 🔐 **Secure Configuration** - Environment-based API key management
- 📊 **Dashboard Interface** - Streamlit-based UI for monitoring and control
- 🤖 **Browser Automation** - Selenium-powered form filling with intelligent field detection
- 📧 **Email Notifications** - Get alerts when jobs are found and applications are sent

## 📁 Project Structure

```
ApplyMate/
├── src/                    # Source code
│   ├── agent.py           # Main job search agent
│   ├── scheduled_automation.py  # Time-based automation
│   ├── enhanced_job_applier.py  # Browser automation
│   ├── enhanced_job_platforms.py # Platform integrations
│   └── resume_parser.py   # AI resume parsing
├── config/                # Configuration files
│   ├── env.example        # Environment template
│   ├── mcp_config.json    # MCP server configuration
│   ├── preferences.json   # Job preferences
│   └── personal_info.example.json
├── scripts/               # Launcher scripts
│   ├── setup.bat/ps1      # Setup scripts
│   └── start_automation.bat/ps1
├── docs/                  # Documentation
│   ├── SETUP_GUIDE.md
│   └── AUTOMATION_GUIDE.md
├── tests/                 # Test files
├── app.py                 # Streamlit dashboard
├── main.py                # CLI entry point
└── requirements.txt       # Dependencies
```

## 🚀 Quick Start

### 1. Setup

```bash
# Run setup script
.\scripts\setup.bat
# OR
.\scripts\setup.ps1

# This will:
# - Create virtual environment
# - Install dependencies
# - Copy configuration templates

# 4. Run agent
python agent.py
# OR dashboard
streamlit run app.py
```

---

## 🔑 Required API Keys

You need these API keys in your `.env` file:

1. **GOOGLE_API_KEY** - Get from Google AI Studio
2. **FIRECRAWL_API_KEY** - Get from Firecrawl.io
3. **BROWSERBASE_API_KEY** - Get from BrowserBase
4. **BROWSERBASE_PROJECT_ID** - Your BrowserBase project ID
5. **EMAIL_USER** - Your Gmail address
6. **EMAIL_PASS** - Gmail app password (not regular password)

### Mail Watcher Additional Configuration (Optional):
- **IMAP_SERVER** - IMAP server address (default: imap.gmail.com)
- **IMAP_PORT** - IMAP port (default: 993)
- **POLL_INTERVAL** - Seconds between inbox checks (default: 60)
- **MAX_APPLICATIONS** - Max jobs to apply per email (default: 3)
- **RESUME_PATH** - Path to resume file (default: temp_resume.pdf)
- **MAIL_FILTER_SENDER** - Only process emails from specific sender
- **MAIL_FILTER_SUBJECT** - Only process emails with subject containing text

---

## 📋 Personal Information Setup

Edit `personal_info.json` with your actual information:
```json
{
  "name": "Your Full Name",
  "email": "your.email@example.com",
  "phone": "+1-xxx-xxx-xxxx",
  "linkedin": "https://linkedin.com/in/yourprofile",
  "cover_letter_template": "Your custom cover letter template..."
}
```

---

## 🎯 Usage Options

### 1. Streamlit Dashboard (Recommended)
- Upload resume
- Configure job preferences
- Run agent with visual feedback
- View results and download CSV

### 2. Direct Agent Run
- Run agent directly from command line
- Good for testing and automation

### 3. Scheduled Time-Based Auto-Apply (RECOMMENDED!)
- **Fully automated**: Searches and applies at scheduled times
- **Browser automation**: Fills ALL form fields automatically
- **Default**: Runs at 9 AM and 6 PM on weekdays
- **Customizable schedule**: Set your own times

```bash
# Use easy launcher
start_automation.bat
# or
.\start_automation.ps1

# Or run directly
python scheduled_automation.py

# Test immediately (no waiting for schedule)
python scheduled_automation.py now
```

### 4. Email-Triggered Auto-Apply (OPTIONAL)
- Monitor your inbox for job notifications
- Automatically apply to jobs from email links
- Perfect for responding to recruiter emails quickly

```bash
# Start the mail watcher
python mail_watcher.py
```

---

## 🔍 What the Agent Does

1. **SEARCHES** job sites (Indeed, LinkedIn, company sites)
2. **SCRAPES** job listings using Firecrawl
3. **FILTERS** jobs based on your criteria
4. **RANKS** jobs by relevance
5. **NOTIFIES** you via email with matches
6. **APPLIES** automatically to top 3 jobs using Selenium
7. **MONITORS** your email inbox for new job opportunities (NEW!)

---

## 📊 Output Files

- `jobs_dashboard.csv` - All filtered job matches
- `applymate.log` - Detailed execution logs
- Email notifications with job summaries

---

## � Email-Triggered Auto-Apply Feature

The **Mail Watcher** monitors your inbox and automatically applies to job links in emails!

### 🎯 How It Works:
1. **Polls** your IMAP inbox for new unread emails
2. **Extracts** job application links from email content
3. **Filters** to only process job-related URLs
4. **Applies** automatically using browser automation
5. **Marks** processed emails as read

### ⚙️ Setup:

1. **Enable IMAP Access** (for Gmail):
   - Go to Gmail Settings → Forwarding and POP/IMAP
   - Enable IMAP access
   - Create an App Password (Settings → Security → 2-Step Verification → App Passwords)

2. **Configure Environment Variables** (in `.env`):
   ```bash
   EMAIL_USER=your.email@gmail.com
   EMAIL_PASS=your-app-password
   IMAP_SERVER=imap.gmail.com
   IMAP_PORT=993
   POLL_INTERVAL=60
   MAX_APPLICATIONS=3
   RESUME_PATH=temp_resume.pdf
   
   # Optional filters
   MAIL_FILTER_SENDER=noreply@linkedin.com
   MAIL_FILTER_SUBJECT=job recommendation
   ```

3. **Run the Mail Watcher**:
   ```bash
   # Continuous monitoring (checks every 60 seconds)
   python mail_watcher.py
   
   # One-time check (process current unread emails and exit)
   set MAIL_WATCHER_MODE=once
   python mail_watcher.py
   ```

### 🎨 Features:
- ✅ **Smart Link Extraction** - Only processes job-related URLs
- ✅ **Filter by Sender/Subject** - Focus on specific job notifications
- ✅ **Rate Limiting** - Delays between applications to avoid detection
- ✅ **Comprehensive Logging** - Track all processed emails and applications
- ✅ **Auto-mark as Read** - Prevents reprocessing the same emails
- ✅ **Platform Detection** - Automatically handles LinkedIn, Indeed, Naukri, etc.

### 📋 Supported Email Sources:
- LinkedIn job notifications
- Indeed job alerts
- Naukri.com notifications
- Recruiter emails with job links
- Company career page notifications
- Any email containing job application URLs

### 💡 Use Cases:
1. **Respond to Recruiter Emails** - Automatically apply when recruiters send job links
2. **Job Alert Automation** - Turn email alerts into instant applications
3. **Quick Apply Mode** - Apply to jobs while you sleep!

---

## �🛠️ Troubleshooting

### Common Issues:
1. **"Missing environment variables"** → Check .env file
2. **"Resume not found"** → Upload resume via dashboard
3. **"Email not sending"** → Use Gmail app password
4. **"MCP tools failing"** → Check API keys and internet

### Debug Mode:
- All operations are logged to `applymate.log`
- Console output shows detailed progress
- Use `DEBUG=1` in .env for verbose logging

---

## 🔒 Security Notes

- ✅ Personal info now stored securely in `personal_info.json`
- ✅ No hardcoded credentials in code
- ✅ Environment variables properly validated
- ✅ Input validation for all user data
- ✅ Comprehensive error handling and logging

---

## 🎉 You're Ready!

Your ApplyMate agent is now secure, properly configured, and ready to automate your job search. The critical security vulnerabilities have been fixed, and you have a robust, production-ready setup.

**Next Step:** Run `streamlit run app.py` and start your automated job search!


