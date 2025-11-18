# 📧 Mail Watcher Quick Start Guide

## What is Mail Watcher?

Mail Watcher is an automated email monitoring system that watches your inbox for job notification emails and automatically applies to job links found in those emails using browser automation.

## 🚀 Quick Setup (5 minutes)

### Step 1: Enable IMAP Access (Gmail)

1. Go to Gmail Settings (⚙️ icon → See all settings)
2. Navigate to **Forwarding and POP/IMAP** tab
3. Enable **IMAP access**
4. Click **Save Changes**

### Step 2: Create App Password (Gmail)

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable **2-Step Verification** (if not already enabled)
3. Navigate to **App Passwords**
4. Select app: **Mail**, device: **Windows Computer**
5. Click **Generate**
6. Copy the 16-character password (remove spaces)

### Step 3: Configure Environment

Edit your `.env` file and add:

```bash
# Required
EMAIL_USER=your.email@gmail.com
EMAIL_PASS=your-16-char-app-password

# Optional (defaults shown)
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
POLL_INTERVAL=60
MAX_APPLICATIONS=3
RESUME_PATH=temp_resume.pdf
```

### Step 4: Test the Setup

Run the test script to verify everything works:

```powershell
python test_mail_watcher.py
```

### Step 5: Start Watching!

```powershell
# Continuous monitoring (runs forever)
python mail_watcher.py

# One-time check (process current emails and exit)
$env:MAIL_WATCHER_MODE="once"
python mail_watcher.py
```

## 🎯 How It Works

```
┌─────────────────┐
│  Your Inbox     │
│  (Gmail/IMAP)   │
└────────┬────────┘
         │
         │ Polls every 60s
         ▼
┌─────────────────┐
│  Mail Watcher   │
│  - Checks unread│
│  - Extracts URLs│
│  - Filters jobs │
└────────┬────────┘
         │
         │ Job URLs found
         ▼
┌─────────────────┐
│ Enhanced Job    │
│ Applier         │
│ - Opens browser │
│ - Fills forms   │
│ - Submits apps  │
└─────────────────┘
```

## 📋 What Emails Are Processed?

The mail watcher looks for job-related URLs in your emails:

### ✅ Processed URLs:
- LinkedIn job posts (`linkedin.com/jobs`)
- Indeed listings (`indeed.com`)
- Naukri.com jobs (`naukri.com`)
- Glassdoor listings (`glassdoor.com`)
- Company career pages with "job", "career", "apply" in URL
- Recruiter email links to job applications

### ❌ Skipped URLs:
- Social media feeds
- Privacy/unsubscribe links
- Help/support pages
- Non-job related content

## 🎨 Advanced Features

### Email Filters

Only process specific emails:

```bash
# Only process LinkedIn notifications
MAIL_FILTER_SENDER=noreply@linkedin.com

# Only process emails with "job recommendation" in subject
MAIL_FILTER_SUBJECT=job recommendation

# Both filters (must match both)
MAIL_FILTER_SENDER=recruiter@company.com
MAIL_FILTER_SUBJECT=urgent position
```

### Custom Configuration

```python
from mail_watcher import MailWatcher

watcher = MailWatcher(
    imap_server='imap.gmail.com',
    imap_port=993,
    poll_interval=30,  # Check every 30 seconds
    max_applications=5,  # Apply to 5 jobs per email
    filter_sender='jobs@linkedin.com',
    filter_subject='recommended for you'
)

# Check once
watcher.check_once()

# Or watch continuously
watcher.start_watching()
```

## 📊 Output and Logs

While running, you'll see:

```
📬 Mail Watcher Started
================================
Server: imap.gmail.com:993
User: your.email@gmail.com
Poll Interval: 60s
================================

👀 Watching for new emails...

📧 Found 1 unseen message(s)

📨 Processing Email
From: jobs@linkedin.com
Subject: 5 new jobs matching your preferences
================================

🔗 Found 5 potential job link(s):
   1. https://www.linkedin.com/jobs/view/123456789
   2. https://www.indeed.com/viewjob?jk=abcdef123
   ...

🚀 Triggering applications (max 3)...

🎯 Applying to: Python Developer at Tech Corp
📱 Platform detected: linkedin
✅ SUCCESS: Applied to Python Developer

📊 Application Results:
   ✅ Successful: 2
   ❌ Failed: 1
   📈 Total Attempted: 3

✔️  Email marked as processed
```

## 🛠️ Troubleshooting

### Issue: "IMAP connection failed"
**Solution:** 
- Verify IMAP is enabled in Gmail settings
- Check EMAIL_USER and EMAIL_PASS are correct
- Use App Password, not regular Gmail password

### Issue: "No unseen messages found"
**Solution:**
- Check if you have unread emails
- Try marking an email as unread to test
- Verify filters aren't too restrictive

### Issue: "No job links found in email"
**Solution:**
- Check email actually contains URLs
- URLs must be job-related (see processed URLs list)
- Try viewing email HTML source to verify links exist

### Issue: "Application failed"
**Solution:**
- Some job sites have strong anti-bot protection
- Check `applymate.log` for detailed errors
- Ensure resume file exists at RESUME_PATH
- Test the job URL manually in `enhanced_job_applier.py`

## 💡 Best Practices

1. **Start with Filters** - Use `MAIL_FILTER_SENDER` or `MAIL_FILTER_SUBJECT` to avoid processing all emails initially

2. **Test with One-Shot Mode** - Use `MAIL_WATCHER_MODE=once` to test before running continuously

3. **Limit Applications** - Set `MAX_APPLICATIONS=1` when testing to avoid mass applications

4. **Monitor Logs** - Check console output and `applymate.log` for issues

5. **Use Dedicated Email** - Consider a separate email account for job searches

6. **Rate Limiting** - Default 10-second delay between applications prevents detection

## 🔐 Security Tips

- ✅ Use Gmail App Passwords (never your main password)
- ✅ Store credentials in `.env` file (never commit to git)
- ✅ Enable 2-Factor Authentication on email account
- ✅ Review applications before submitting (set `MAX_APPLICATIONS=1` for testing)
- ✅ Monitor the `jobs_dashboard.csv` for application history

## 🎯 Example Use Cases

### Use Case 1: LinkedIn Job Alerts
```bash
MAIL_FILTER_SENDER=noreply@linkedin.com
MAIL_FILTER_SUBJECT=recommended for you
MAX_APPLICATIONS=3
POLL_INTERVAL=300  # Check every 5 minutes
```

### Use Case 2: Recruiter Emails
```bash
MAIL_FILTER_SUBJECT=urgent position
MAX_APPLICATIONS=1
POLL_INTERVAL=60  # Check every minute
```

### Use Case 3: All Job Notifications
```bash
# No filters - process all emails with job links
MAX_APPLICATIONS=5
POLL_INTERVAL=120  # Check every 2 minutes
```

## 📞 Support

If you encounter issues:
1. Check `applymate.log` for detailed error messages
2. Run `python test_mail_watcher.py` to diagnose configuration
3. Review the Troubleshooting section above
4. Check README.md for general ApplyMate setup

---

**Happy Auto-Applying! 🚀**

The Mail Watcher will help you respond to job opportunities faster than ever!
