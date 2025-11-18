# Stagehand MCP Integration Guide

## Overview
ApplyMate now uses **Stagehand MCP** for natural language browser automation, replacing traditional Selenium-based automation with AI-powered intelligent form filling.

## What is Stagehand?
Stagehand is an MCP (Model Context Protocol) server that provides browser automation through natural language commands. Instead of writing CSS selectors and explicit element interactions, you describe what you want to do in plain English.

## Benefits Over Selenium
- ✅ **Natural Language** - "Click the Apply button" vs finding CSS selectors
- ✅ **More Reliable** - Adapts to UI changes automatically
- ✅ **Intelligent** - Understands context and intent
- ✅ **Less Maintenance** - No brittle selectors to update
- ✅ **Better Error Handling** - AI can retry with different strategies

## Setup

### 1. Configure MCP Server
Copy `config/mcp_config.example.json` to `config/mcp_config.json`:

```json
{
  "mcpServers": {
    "stagehand": {
      "command": "npx",
      "args": ["-y", "@stagehand/mcp-server"],
      "env": {
        "BROWSERBASE_API_KEY": "your-api-key",
        "BROWSERBASE_PROJECT_ID": "your-project-id"
      }
    }
  }
}
```

### 2. Get BrowserBase Credentials
1. Visit https://browserbase.com
2. Sign up for free account
3. Get API key and Project ID
4. Add to `mcp_config.json`

### 3. Install Node.js (if not installed)
Stagehand requires Node.js to run:
- Download from https://nodejs.org
- Verify: `node --version`

## Usage

### Programmatic Usage

```python
from src.stagehand_automation import StagehandAutomation
import asyncio

async def main():
    automation = StagehandAutomation()
    await automation.initialize()
    
    # Apply to a job
    job = {
        'title': 'AI Engineer Intern',
        'company': 'Tech Company',
        'link': 'https://example.com/careers/job/123'
    }
    
    personal_info = {
        'name': 'John Doe',
        'email': 'john@example.com',
        'phone': '+1-234-567-8900',
        'linkedin': 'https://linkedin.com/in/johndoe'
    }
    
    result = await automation.apply_to_job(
        job=job,
        personal_info=personal_info,
        resume_path='temp_resume.pdf'
    )
    
    print(f"Success: {result['success']}")
    print(f"Details: {result['details']}")
    
    await automation.close()

asyncio.run(main())
```

### Batch Applications

```python
# Apply to multiple jobs
jobs = [
    {'title': 'Job 1', 'company': 'Company A', 'link': 'url1'},
    {'title': 'Job 2', 'company': 'Company B', 'link': 'url2'},
]

results = await automation.batch_apply(
    jobs=jobs,
    personal_info=personal_info,
    resume_path='temp_resume.pdf',
    max_applications=5  # Apply to max 5 jobs
)

# Results contains success/failure status for each application
```

### Scheduled Automation
The scheduled automation (`src/scheduled_automation.py`) automatically uses Stagehand:

```bash
# Run scheduled automation
python src/scheduled_automation.py

# Or use launcher
.\scripts\start_automation.ps1
```

## How It Works

### Natural Language Commands
Stagehand translates natural language into browser actions:

```python
# Instead of:
driver.find_element(By.CSS_SELECTOR, "#apply-button").click()

# You write:
"Find and click the Apply button"
```

### Intelligent Form Filling
The AI understands form context:

```python
# It knows these are related:
"Fill in my name: John Doe"
"Fill in email: john@example.com"
"Upload resume from temp_resume.pdf"
"Answer 'Yes' to willing to relocate"
```

### Safety Features
- **Review Before Submit** - Stops at review page, doesn't auto-submit
- **Screenshots** - Takes screenshots of filled forms
- **Error Recovery** - Retries with different strategies if something fails
- **Logging** - Detailed logs of all actions

## Troubleshooting

### "Connection refused" Error
- Check Node.js is installed: `node --version`
- Verify MCP config path is correct
- Check BrowserBase credentials

### "Tool not found" Error
- Ensure `@stagehand/mcp-server` is available
- Try: `npx -y @stagehand/mcp-server --help`

### Application Not Completing
- Check logs for specific errors
- Verify job URL is accessible
- Ensure personal_info.json has all required fields

### Rate Limiting
- BrowserBase has rate limits
- Add delays between applications (default: 30 seconds)
- Use `max_applications` to limit batch size

## Advanced Features

### Extract Job Details
```python
details = await automation.extract_job_details(job_url)
print(details['data'])  # Contains title, salary, requirements, etc.
```

### Custom Prompts
Modify prompts in `src/stagehand_automation.py` for specific needs:

```python
# Customize application behavior
prompt = f"""
Navigate to {job_url} and:
1. Click Apply
2. Fill form with {personal_info}
3. Skip salary questions
4. Stop before submit
"""
```

## Cost Considerations
- BrowserBase: ~$0.01-0.05 per application session
- Gemini API: ~$0.001 per application
- Total: ~$0.01-0.06 per job application

## Best Practices
1. **Test First** - Run on test URLs before production
2. **Monitor Logs** - Check logs for errors and improvements
3. **Gradual Rollout** - Start with 1-2 applications, scale up
4. **Verify Forms** - Check screenshots to ensure accuracy
5. **Update Personal Info** - Keep personal_info.json current

## Migration from Selenium
If migrating from Selenium-based automation:

1. Old code in `src/enhanced_job_applier.py` (legacy)
2. New code in `src/stagehand_automation.py` (current)
3. Scheduled automation automatically uses new system
4. Both can coexist during transition

## Support
- Stagehand Docs: https://docs.stagehand.dev
- BrowserBase Docs: https://docs.browserbase.com
- MCP Protocol: https://modelcontextprotocol.io

---

**Ready to automate!** 🚀
