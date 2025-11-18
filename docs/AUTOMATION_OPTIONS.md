# 🎯 ApplyMate Automation Options - Choose Your Style

## Three Ways to Automate Job Applications

---

## Option 1: ⏰ Time-Based Automation (RECOMMENDED!)

### What It Does:
✅ Runs at **scheduled times** (9 AM, 6 PM weekdays)  
✅ **Searches** job sites automatically  
✅ **Fills ALL forms** via browser automation  
✅ **No email** monitoring needed  
✅ **Fully automated** - set it and forget it

### When To Use:
- ✅ You want hands-off automation
- ✅ You want predictable application times
- ✅ You want to apply to many jobs automatically
- ✅ You don't want to monitor emails

### How To Run:
```powershell
# Start scheduler
python scheduled_automation.py

# Or test immediately
python scheduled_automation.py now
```

### Configuration:
```bash
# In .env
SCHEDULE_HOUR=9
SCHEDULE_MINUTE=0
SCHEDULE_DAYS=mon-fri
MAX_APPLICATIONS_PER_RUN=5
```

**📁 Main File:** `scheduled_automation.py`  
**📖 Guide:** `AUTOMATION_GUIDE.md`

---

## Option 2: 📧 Email-Triggered Automation (OPTIONAL)

### What It Does:
✅ **Monitors** your inbox for job emails  
✅ **Extracts** job links from emails  
✅ **Applies** to jobs found in emails  
✅ Great for **recruiter emails**  

### When To Use:
- ✅ You get recruiter emails with job links
- ✅ You want to respond to emails quickly
- ✅ You want targeted applications
- ✅ You subscribe to job alerts

### How To Run:
```powershell
# Start email watcher
python mail_watcher.py

# Or check once
$env:MAIL_WATCHER_MODE="once"
python mail_watcher.py
```

### Configuration:
```bash
# In .env
EMAIL_USER=your@email.com
EMAIL_PASS=your-app-password
IMAP_SERVER=imap.gmail.com
POLL_INTERVAL=60
```

**📁 Main File:** `mail_watcher.py`  
**📖 Guide:** `MAIL_WATCHER_GUIDE.md`

---

## Option 3: 🖥️ Manual Dashboard (INTERACTIVE)

### What It Does:
✅ **Web interface** via Streamlit  
✅ **Manual control** of searches  
✅ **Visual dashboard** for results  
✅ **Upload resume** via UI  

### When To Use:
- ✅ You want visual control
- ✅ You want to review before applying
- ✅ You prefer interactive interface
- ✅ You're learning the system

### How To Run:
```powershell
# Start dashboard
streamlit run app.py
```

**📁 Main File:** `app.py`  
**📖 Guide:** `README.md`

---

## 📊 Comparison Table

| Feature | Time-Based | Email-Triggered | Manual Dashboard |
|---------|------------|-----------------|------------------|
| **Fully Automated** | ✅ Yes | ✅ Yes | ❌ No |
| **Scheduled Runs** | ✅ Yes | ❌ No | ❌ No |
| **Email Monitoring** | ❌ No | ✅ Yes | ❌ No |
| **Visual Interface** | ❌ No | ❌ No | ✅ Yes |
| **Browser Automation** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Fills All Fields** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Resume Upload** | ✅ Auto | ✅ Auto | ✅ Manual |
| **Job Search** | ✅ Auto | ❌ From emails | ✅ Manual |
| **Best For** | 24/7 automation | Recruiter emails | Learning/testing |
| **Setup Complexity** | ⭐⭐ Medium | ⭐⭐⭐ Higher | ⭐ Simple |
| **Hands-Off Level** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ |

---

## 🎯 Which One Should You Use?

### Use **Time-Based Automation** if:
- ✅ You want to apply to 10-50 jobs/week automatically
- ✅ You want predictable morning/evening runs
- ✅ You don't want to monitor emails
- ✅ You want maximum automation

**👉 Start here:** `python scheduled_automation.py now`

---

### Use **Email-Triggered** if:
- ✅ You get many job notification emails
- ✅ You want to respond to recruiters fast
- ✅ You subscribe to Indeed/LinkedIn alerts
- ✅ You want targeted applications only

**👉 Start here:** `python mail_watcher.py`

---

### Use **Manual Dashboard** if:
- ✅ You're new to ApplyMate
- ✅ You want to see what it does
- ✅ You prefer visual interfaces
- ✅ You want to review before applying

**👉 Start here:** `streamlit run app.py`

---

## 💡 Recommended Approach

### For Maximum Results:
**Use Time-Based Automation as primary**
```powershell
# Set up once
python scheduled_automation.py

# Runs automatically at:
# - 9 AM weekdays → Search and apply
# - 6 PM weekdays → Search and apply
```

**Result:** 10 applications/day = 50/week = ~200/month

### For Recruiter Emails (Optional Add-on):
**Add Email-Triggered on top**
```powershell
# Run in separate terminal
python mail_watcher.py
```

**Result:** Extra 2-5 applications/day from recruiter emails

---

## 🚀 Quick Start Guide

### Step 1: Configure (5 minutes)
```bash
# Edit .env
EMAIL_USER=your@email.com
EMAIL_PASS=your-app-password
RESUME_PATH=temp_resume.pdf

# Edit preferences.json
{
  "title": "Python Developer",
  "location": "Remote",
  "skills": ["Python", "Django"],
  "min_salary": 80000
}

# Edit personal_info.json
{
  "name": "Your Name",
  "email": "your@email.com",
  "phone": "+1-234-567-8900"
}
```

### Step 2: Test Time-Based (2 minutes)
```powershell
# Run immediately to see it work
python scheduled_automation.py now
```

### Step 3: Start Automation (forever)
```powershell
# Let it run automatically
python scheduled_automation.py
```

Done! Now it applies to jobs twice daily automatically.

---

## 📁 File Guide

| File | Purpose | Use When |
|------|---------|----------|
| `scheduled_automation.py` | Time-based automation | Main automation |
| `mail_watcher.py` | Email monitoring | Optional add-on |
| `app.py` | Web dashboard | Testing/learning |
| `agent.py` | Core job agent | Called by others |
| `enhanced_job_applier.py` | Browser automation | Used by all |
| `start_automation.bat` | Easy launcher | Windows users |

---

## 🎓 Learning Path

### Day 1: Learn the System
```powershell
# Start dashboard to see it work
streamlit run app.py
# Upload resume, run search, see results
```

### Day 2: Test Automation
```powershell
# Test time-based automation
python scheduled_automation.py now
# Watch it search and apply
```

### Day 3: Go Automatic
```powershell
# Start scheduled automation
python scheduled_automation.py
# Let it run 24/7
```

### Optional: Add Email Monitoring
```powershell
# If you get recruiter emails
python mail_watcher.py
```

---

## 🎯 Expected Results Per Option

### Time-Based (Recommended):
- **Schedule**: 9 AM + 6 PM weekdays
- **Per Run**: 5 applications
- **Per Day**: 10 applications
- **Per Week**: 50 applications
- **Per Month**: ~200 applications

### Email-Triggered:
- **Depends on**: Email frequency
- **Typical**: 2-5 applications/day
- **Per Week**: 10-25 applications
- **Per Month**: ~40-100 applications

### Manual Dashboard:
- **Depends on**: Your usage
- **Typical**: 5-10 applications/session
- **Requires**: Manual running

### Combined (Time + Email):
- **Per Day**: 12-15 applications
- **Per Week**: 60-75 applications
- **Per Month**: ~250-300 applications

---

## 🔧 Troubleshooting

### Time-Based Not Running?
```powershell
# Test configuration
python scheduled_automation.py test

# Run immediately to debug
python scheduled_automation.py now

# Check logs
type applymate.log
```

### Email-Triggered Not Working?
```powershell
# Test configuration
python test_mail_watcher.py

# Check email credentials
# Verify IMAP is enabled in Gmail
```

### Applications Failing?
- Check `personal_info.json` - ensure all fields filled
- Verify resume file exists at `RESUME_PATH`
- Look at `applymate.log` for errors
- Try fewer platforms first

---

## 📞 Need Help?

**Configuration Issues:**
- See: `AUTOMATION_GUIDE.md`
- Check: `.env.example` for required variables

**Email Setup Issues:**
- See: `MAIL_WATCHER_GUIDE.md`
- Use Gmail App Password (not regular password)

**Application Errors:**
- Check: `applymate.log`
- Run: `python scheduled_automation.py now` to debug

**General Setup:**
- See: `README.md`
- See: `SETUP_GUIDE.md`

---

## ✨ Bottom Line

**For most users:**
```powershell
# Just run this
python scheduled_automation.py

# It will automatically:
# ✅ Search for jobs twice daily
# ✅ Filter by your preferences
# ✅ Apply via browser automation
# ✅ Fill ALL form fields
# ✅ Upload resume
# ✅ Email you results
```

**That's it! Set it once, let it run forever.**

---

*For your use case: "browser automation at triggered time that fills all details"*

**👉 Use: Time-Based Automation (`scheduled_automation.py`)**

**It does exactly what you asked:**
- ⏰ Triggered at specific times
- 🌐 Browser automation
- 📝 Fills ALL details automatically
- ✅ No email monitoring needed
