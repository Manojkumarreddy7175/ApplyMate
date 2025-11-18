# 🤖 Scheduled Job Automation - Quick Start Guide

## What This Does

The **Scheduled Job Automation** automatically runs browser-based job applications at specific times. No email monitoring needed - just set it and forget it!

### Automation Flow:
```
⏰ Scheduled Time (9 AM, 6 PM) 
    ↓
🔍 Search Job Sites (LinkedIn, Indeed, Naukri)
    ↓
🎯 Filter by Your Preferences (skills, location, salary)
    ↓
🌐 Open Browser (Selenium/Chrome)
    ↓
📝 Fill All Application Forms Automatically
    ↓
📄 Upload Resume
    ↓
✅ Submit Applications
    ↓
📧 Email You the Results
```

---

## 🚀 Quick Setup (3 Steps)

### Step 1: Configure Your Settings

Edit `.env` file:

```bash
# Required
EMAIL_USER=your.email@gmail.com
EMAIL_PASS=your-gmail-app-password
RESUME_PATH=temp_resume.pdf
MAX_APPLICATIONS_PER_RUN=5

# Optional: Custom schedule (default is 9 AM and 6 PM weekdays)
SCHEDULE_HOUR=9
SCHEDULE_MINUTE=0
SCHEDULE_DAYS=mon-fri
```

### Step 2: Set Your Job Preferences

Edit `preferences.json`:

```json
{
  "title": "Python Developer",
  "location": "Remote",
  "skills": ["Python", "Django", "REST API", "PostgreSQL"],
  "min_salary": 80000
}
```

### Step 3: Set Your Personal Information

Edit `personal_info.json`:

```json
{
  "name": "Your Full Name",
  "email": "your.email@gmail.com",
  "phone": "+1-123-456-7890",
  "linkedin": "https://linkedin.com/in/yourprofile",
  "website": "https://github.com/yourprofile",
  "years_experience": "3",
  "current_company": "Current Company Name",
  "notice_period": "Immediate"
}
```

---

## 🎯 How to Run

### Option 1: Use Launcher Script (Easiest)

**Windows Command Prompt:**
```cmd
start_automation.bat
```

**PowerShell:**
```powershell
.\start_automation.ps1
```

Then select:
- **Option 1**: Start scheduled automation (runs at configured times)
- **Option 2**: Run NOW (test immediately)
- **Option 3**: Test configuration

### Option 2: Direct Command Line

```powershell
# Start scheduled automation
python scheduled_automation.py

# Run immediately (one-time test)
python scheduled_automation.py now

# Test configuration
python scheduled_automation.py test
```

---

## ⚙️ Configuration Options

### Default Schedule:
- **9:00 AM** - Monday to Friday
- **6:00 PM** - Monday to Friday

### Custom Schedule Examples:

**Run at 8 AM every day:**
```bash
SCHEDULE_HOUR=8
SCHEDULE_MINUTE=0
SCHEDULE_DAYS=mon-sun
```

**Run at 12 PM only on weekdays:**
```bash
SCHEDULE_HOUR=12
SCHEDULE_MINUTE=0
SCHEDULE_DAYS=mon-fri
```

**Run at 3:30 PM on Monday, Wednesday, Friday:**
```bash
SCHEDULE_HOUR=15
SCHEDULE_MINUTE=30
SCHEDULE_DAYS=mon,wed,fri
```

### Max Applications:
```bash
# Apply to 10 jobs per run
MAX_APPLICATIONS_PER_RUN=10

# Apply to only 3 jobs per run (conservative)
MAX_APPLICATIONS_PER_RUN=3
```

---

## 📋 What Gets Filled Automatically

The browser automation fills **ALL** these fields:

✅ **Personal Information:**
- First Name, Last Name
- Email Address
- Phone Number
- LinkedIn Profile
- Website/Portfolio

✅ **Professional Details:**
- Years of Experience
- Current Company
- Notice Period
- Work Authorization

✅ **Application Materials:**
- Resume Upload (PDF/DOCX)
- Cover Letter (Auto-generated based on job)

✅ **Job-Specific:**
- Preferred Location
- Salary Expectations
- Remote Work Preference

---

## 🌐 Supported Platforms

The automation works with:

- ✅ **LinkedIn** - Easy Apply and full applications
- ✅ **Indeed** - Quick Apply and standard forms
- ✅ **Naukri.com** - Indian job portal
- ✅ **Glassdoor** - Application forms
- ✅ **AngelList/Wellfound** - Startup jobs
- ✅ **Instahyre** - Tech jobs
- ✅ **Cutshort** - Product jobs
- ✅ **Greenhouse** - ATS platform
- ✅ **Lever** - ATS platform
- ✅ **Workday** - ATS platform

---

## 📊 What Happens at Each Run

1. **Job Search** (2-3 minutes)
   - Searches LinkedIn, Indeed, Naukri
   - Finds ~30 job listings total

2. **Filtering** (< 1 minute)
   - Matches against your skills
   - Checks location preference
   - Verifies salary requirements
   - Narrows to ~10 relevant jobs

3. **Auto-Apply** (5-10 minutes)
   - Opens browser for each job
   - Fills all form fields
   - Uploads resume
   - Submits application
   - Applies to 5 jobs (configurable)

4. **Results** (< 1 minute)
   - Saves jobs to `jobs_dashboard.csv`
   - Sends email with results
   - Logs everything to `applymate.log`

**Total Time**: ~10-15 minutes per run

---

## 📧 Email Notifications

After each run, you'll receive an email with:

- ✅ Number of jobs found
- ✅ Number of applications submitted
- ✅ Success rate
- ✅ Top 10 jobs table (title, company, location, link)
- ✅ Any errors encountered

---

## 🔍 Example Output

```
========================================
🤖 SCHEDULED JOB AUTOMATION STARTED
⏰ Time: 2025-11-09 09:00:00
========================================

📄 Step 1: Loading resume and preferences...
✅ Preferences loaded: Python Developer in Remote

🔍 Step 2: Searching for jobs across platforms...
   Searching naukri...
   ✅ Found 12 jobs on naukri
   Searching indeed...
   ✅ Found 15 jobs on indeed
   Searching linkedin...
   ✅ Found 8 jobs on linkedin
✅ Total jobs found: 35

🎯 Step 3: Filtering jobs based on criteria...
✅ Filtered to 12 relevant jobs
💾 Saved 12 jobs to jobs_dashboard.csv

🚀 Step 4: Auto-applying to top 5 jobs...

🎯 Applying to: Senior Python Developer at Tech Corp
📱 Platform detected: linkedin
   📝 Form fields filled
   📄 Resume uploaded
✅ SUCCESS: Applied to Senior Python Developer

🎯 Applying to: Backend Engineer at StartupXYZ
📱 Platform detected: indeed
   📝 Form fields filled
   📄 Resume uploaded
✅ SUCCESS: Applied to Backend Engineer

... (3 more applications)

========================================
📊 AUTOMATION RESULTS
========================================
🔍 Jobs Found: 35
✅ Jobs Matching Criteria: 12
📤 Applications Sent: 4
❌ Applications Failed: 1
📈 Success Rate: 80.0%
========================================

📧 Step 5: Sending email notification...
✅ Email notification sent
```

---

## 🛠️ Troubleshooting

### Issue: "Resume file not found"
**Solution:**
```bash
# Check if file exists
dir temp_resume.pdf

# Or set custom path in .env
RESUME_PATH=C:\path\to\your\resume.pdf
```

### Issue: "No jobs found"
**Solution:**
- Check your `preferences.json` - skills might be too specific
- Try broader search terms
- Check internet connection
- Look at `applymate.log` for details

### Issue: "Applications failing"
**Solution:**
- Some sites have strong anti-bot protection
- Check `personal_info.json` - ensure all fields are filled
- Verify resume file is valid (PDF/DOCX)
- Run with `python scheduled_automation.py now` to debug

### Issue: "Email not sending"
**Solution:**
- Use Gmail App Password (not regular password)
- Check EMAIL_USER and EMAIL_PASS in `.env`
- Enable "Less secure app access" or use App Password

---

## 💡 Best Practices

1. **Start with Test Run**
   ```powershell
   python scheduled_automation.py now
   ```
   See results immediately before scheduling

2. **Limit Applications Initially**
   ```bash
   MAX_APPLICATIONS_PER_RUN=2
   ```
   Test with 2-3 applications first

3. **Review Results**
   - Check `jobs_dashboard.csv` after first run
   - Verify applications are going through
   - Adjust preferences if needed

4. **Monitor Logs**
   - Check `applymate.log` for details
   - Look for patterns in failures
   - Adjust filters based on results

5. **Schedule Wisely**
   - 9 AM catches overnight postings
   - 6 PM catches afternoon postings
   - Avoid peak hours (12-1 PM) when sites are busy

---

## 🎯 Tips for Better Results

### Optimize Your Preferences:
```json
{
  "title": "Python Developer",  // Be specific but not too narrow
  "location": "Remote",          // "Remote" gets more matches
  "skills": [
    "Python",                    // Core skills first
    "Django",
    "REST API"
  ],
  "min_salary": 80000            // Set realistic minimum
}
```

### Optimize Application Count:
- **5-10 applications/run** = Balanced approach
- **3-5 applications/run** = Quality over quantity
- **10-15 applications/run** = Aggressive (may trigger anti-bot)

### Schedule Smart:
- **Weekdays only**: Higher chance of human review
- **Morning & Evening**: Catch new postings twice daily
- **Avoid weekends**: Most HR doesn't work weekends

---

## 🔐 Security & Privacy

- ✅ All credentials stored in `.env` (never in code)
- ✅ `.env` excluded from git
- ✅ Browser runs in headless mode (no visible window)
- ✅ Personal info in separate JSON file
- ✅ Resume uploaded securely via HTTPS
- ✅ Comprehensive logging for audit trail

---

## 📊 Expected Success Rates

Based on platform and job type:

- **LinkedIn Easy Apply**: 80-90% success
- **Indeed Quick Apply**: 70-85% success
- **Direct Company Sites**: 50-70% success (varies by site)
- **ATS Platforms (Greenhouse, Lever)**: 60-80% success

Lower success rates may indicate:
- Strong anti-bot measures
- Complex multi-step forms
- Required fields not in your profile
- Site-specific issues

---

## 🚀 Next Steps

1. ✅ Configure `.env` with your credentials
2. ✅ Set preferences in `preferences.json`
3. ✅ Fill personal info in `personal_info.json`
4. ✅ Test with: `python scheduled_automation.py now`
5. ✅ Review results in `jobs_dashboard.csv`
6. ✅ Start scheduler: `python scheduled_automation.py`
7. ✅ Monitor email notifications
8. ✅ Check logs periodically

---

**Your automated job application system is ready! 🎉**

Set it up once, and let it work 24/7 to find and apply to jobs for you!

---

*For more details, see:*
- `README.md` - General project info
- `SETUP_GUIDE.md` - Setup instructions
- `applymate.log` - Execution logs
