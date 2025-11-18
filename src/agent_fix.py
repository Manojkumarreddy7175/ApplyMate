#!/usr/bin/env python3
"""
Fixed version of the job agent that properly handles async operations
"""
import asyncio
import json
import os
import pandas as pd
import re
import logging
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from mcp_use import MCPAgent, MCPClient, set_debug
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
from job_applier import apply_to_jobs
from resume_parser import parse_resume

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global configurations
load_dotenv()
set_debug(1)  # Reduce debug output

def parse_agent_result(agent_result):
    """Parse the agent result to extract jobs data."""
    jobs_list = []
    number_applied = 0

    try:
        # Look for JSON data in the result
        json_pattern = r'```json\s*(\[.*?\])\s*```'
        matches = re.findall(json_pattern, agent_result, re.DOTALL)

        if matches:
            for match in matches:
                try:
                    parsed_jobs = json.loads(match)
                    if isinstance(parsed_jobs, list):
                        jobs_list.extend(parsed_jobs)
                    elif isinstance(parsed_jobs, dict) and 'jobs' in parsed_jobs:
                        jobs_list.extend(parsed_jobs['jobs'])
                except json.JSONDecodeError:
                    continue
    except:
        pass

    # Manual parsing if no JSON found
    if not jobs_list:
        lines = agent_result.split('\n')
        current_job = {}

        for line in lines:
            line = line.strip()
            if 'title:' in line.lower() or line.startswith('- '):
                if current_job and len(current_job) >= 3:
                    jobs_list.append(current_job)
                current_job = {}

                title_match = re.search(r'title:?\s*(.+)', line, re.IGNORECASE)
                current_job['title'] = title_match.group(1).strip() if title_match else line.replace('- ', '').strip()

            elif 'company:' in line.lower():
                company_match = re.search(r'company:?\s*(.+)', line, re.IGNORECASE)
                if company_match:
                    current_job['company'] = company_match.group(1).strip()

            elif 'location:' in line.lower():
                location_match = re.search(r'location:?\s*(.+)', line, re.IGNORECASE)
                if location_match:
                    current_job['location'] = location_match.group(1).strip()

            elif 'link:' in line.lower() or 'url:' in line.lower():
                link_match = re.search(r'(?:link|url):?\s*(http.+)', line, re.IGNORECASE)
                if link_match:
                    current_job['link'] = link_match.group(1).strip()

            elif 'description:' in line.lower():
                desc_match = re.search(r'description:?\s*(.+)', line, re.IGNORECASE)
                if desc_match:
                    current_job['description'] = desc_match.group(1).strip()
                    if len(current_job) >= 3:
                        jobs_list.append(current_job)
                        current_job = {}

        if current_job and len(current_job) >= 3:
            jobs_list.append(current_job)

    # Fill missing fields
    for job in jobs_list:
        job.setdefault('title', 'Unknown Position')
        job.setdefault('company', 'Unknown Company')
        job.setdefault('location', 'Remote')
        job.setdefault('link', '')
        job.setdefault('description', '')
        if 'salary' not in job:
            salary_match = re.search(r'\$[\d,]+(?:k|-[\d,]+k?)', job.get('description', ''), re.IGNORECASE)
            job['salary'] = salary_match.group() if salary_match else 'Not specified'

    return jobs_list, number_applied

def evaluate_job_relevance(job_data, cv_skills, preferences):
    """Evaluate job relevance based on CV skills and preferences."""
    score = 0
    description = job_data.get('description', '').lower()
    title = job_data.get('title', '').lower()

    # Skills matching
    for skill in cv_skills:
        if skill.lower() in description or skill.lower() in title:
            score += 1

    # Salary check
    min_salary = preferences.get('min_salary', 0)
    salary_text = job_data.get('salary', '')
    if salary_text and salary_text != 'not specified' and salary_text != 'Not specified':
        # Handle None type
        if salary_text is None:
            salary_text = ''

        salary_text = salary_text.lower()
        if 'k' in salary_text:
            try:
                salary_num = int(salary_text.replace('$', '').replace('k', '').replace(',', '')) * 1000
                if salary_num >= min_salary:
                    score += 1
            except ValueError:
                pass

    # Location preference
    job_location = job_data.get('location', '')
    if job_location is None:
        job_location = ''

    job_location = job_location.lower()
    pref_location = preferences.get('location', '').lower()
    if pref_location in job_location or 'remote' in job_location:
        score += 0.5

    return score >= 1.5

async def collect_preferences(resume_data):
    """Create preferences from resume data."""
    prefs = {
        "title": resume_data.get("preferred role", "Software Engineer intern"),
        "location": resume_data.get("location", "Remote"),
        "skills": resume_data.get("skills", ["Python", "Java"]),
        "min_salary": resume_data.get("minimum salary expectation", 50000)
    }

    with open('preferences.json', 'w') as f:
        json.dump(prefs, f, indent=2)

    return prefs

async def search_and_process_jobs(prefs, max_retries=3):
    """Search for jobs and process results."""
    client = None
    try:
        # Initialize MCP client
        client = MCPClient.from_config_file("mcp_config.json")
        os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY", "")
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)

        # Create agent
        agent = MCPAgent(llm=llm, client=client, max_steps=50, verbose=False)

        # Construct targeted search queries for job boards
        base_skills = ' '.join(prefs['skills'][:3])  # Use top 3 skills
        location = prefs['location'].replace(', Remote', '').replace('Remote', '')

        # Create multiple targeted search queries
        search_queries = [
            f"site:linkedin.com/jobs {prefs['title']} {location} {base_skills}",
            f"site:indeed.com {prefs['title']} {location} {base_skills}",
            f"site:naukri.com {prefs['title']} {location} {base_skills}",
            f"site:glassdoor.com {prefs['title']} {location} {base_skills}",
            f"{prefs['title']} {location} {base_skills} salary >{prefs['min_salary']}"
        ]

        all_jobs = []

        for query in search_queries[:3]:  # Try first 3 targeted queries
            try:
                logger.info(f"Job search with targeted query: {query}")

                # Execute targeted search
                prompt = f"""
                Search for job listings using this specific query: {query}
                Limit: 5 results per query
                Sources: web only
                Focus on job board career pages and company career sites

                For each result, extract:
                - title: exact job title from the posting
                - company: company name
                - location: job location (city, state, or remote)
                - link: direct link to the job application page
                - description: job description and requirements
                - salary: salary information if mentioned

                Prioritize results from:
                - linkedin.com/jobs
                - indeed.com
                - naukri.com
                - glassdoor.com
                - company career pages

                Return ONLY valid JSON array of job objects, no markdown formatting.
                """

                result = await agent.run(prompt)
                jobs_data, _ = parse_agent_result(result)

                if jobs_data:
                    logger.info(f"Found {len(jobs_data)} jobs from query: {query}")
                    all_jobs.extend(jobs_data)

                    # If we have enough jobs, break early
                    if len(all_jobs) >= 8:
                        break

            except Exception as e:
                logger.warning(f"Search query '{query}' failed: {e}")
                continue

        # Remove duplicates based on title and company
        seen = set()
        unique_jobs = []
        for job in all_jobs:
            key = (job.get('title', ''), job.get('company', ''))
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)

        logger.info(f"Total unique jobs found: {len(unique_jobs)}")
        return unique_jobs

    finally:
        if client:
            await client.close_all_sessions()

async def process_jobs_and_apply(jobs_data, prefs, resume_path):
    """Filter jobs and attempt applications."""
    cv_skills = prefs['skills']

    # Filter relevant jobs
    filtered_jobs = [job for job in jobs_data if evaluate_job_relevance(job, cv_skills, prefs)]
    logger.info(f"Filtered to {len(filtered_jobs)} relevant jobs")

    # Save to CSV
    df = pd.DataFrame(filtered_jobs, columns=['title', 'company', 'location', 'link', 'description', 'salary'])
    df.to_csv('jobs_dashboard.csv', index=False)
    logger.info("Jobs saved to jobs_dashboard.csv")

    # Send email alert
    try:
        send_email_alert(df)
        logger.info("Email alert sent")
    except Exception as e:
        logger.error(f"Email sending failed: {e}")

    # Auto-apply to top jobs (FIXED: synchronous approach)
    applied_count = 0
    if filtered_jobs:
        logger.info(f"Evaluating {len(filtered_jobs)} jobs for auto-application...")
        try:
            applied_count = apply_to_jobs(filtered_jobs, cv_skills, prefs, resume_path, max_applications=3)
            logger.info(f"Successfully applied to {applied_count} jobs")

        except Exception as e:
            logger.error(f"Job application failed: {e}")

    return len(filtered_jobs), applied_count

def send_email_alert(df):
    """Send email alert about found jobs."""
    sender = os.getenv('EMAIL_USER')
    password = os.getenv('EMAIL_PASS')

    if not sender or not password:
        logger.warning("Email credentials not configured")
        return

    msg = MIMEMultipart('alternative')
    msg['From'] = sender
    msg['To'] = sender

    if len(df) > 0:
        msg['Subject'] = f"🎯 {len(df)} New Job Matches Found!"
        html = f"""
        <html>
        <body>
            <h2>🚀 ApplyMate Job Search Results</h2>
            <p>Found {len(df)} jobs matching your preferences:</p>
            {df[['title', 'company', 'location', 'link']].to_html(index=False, escape=False)}
            <br><hr>
            <p><small>ApplyMate automated job search - {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}</small></p>
        </body>
        </html>
        """
    else:
        msg['Subject'] = "ApplyMate: No Matching Jobs Found"
        html = "<h2>No new job matches found this time. We'll keep searching!</h2>"

    msg.attach(MIMEText(html, 'html'))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(sender, password)
            server.sendmail(sender, sender, msg.as_string())
        logger.info(f"Email sent to {sender}")
    except Exception as e:
        logger.error(f"Email sending failed: {e}")

async def run_applymate_job_agent(resume_path="manoj_resume.txt"):
    """Complete ApplyMate workflow: parse resume -> search jobs -> apply."""
    try:
        logger.info("🚀 Starting ApplyMate Job Agent...")

        # Step 1: Parse resume
        logger.info("📄 Parsing resume...")
        resume_data = await parse_resume(resume_path)
        logger.info(f"✅ Resume parsed: {resume_data}")

        # Step 2: Build preferences
        logger.info("⚙️ Building search preferences...")
        prefs = await collect_preferences(resume_data)
        logger.info(f"✅ Preferences: {prefs}")

        # Step 3: Search for jobs
        logger.info("🔍 Searching for jobs...")
        jobs_data = await search_and_process_jobs(prefs)

        # Step 4: Process and apply
        jobs_found, applied_count = await process_jobs_and_apply(jobs_data, prefs, resume_path)

        logger.info("🎉 ApplyMate run completed!")
        return {
            "jobs_found": jobs_found,
            "applied_count": applied_count,
            "resume_data": resume_data,
            "preferences": prefs
        }

    except Exception as e:
        logger.error(f"❌ ApplyMate run failed: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "jobs_found": 0,
            "applied_count": 0
        }

if __name__ == "__main__":
    # Run the complete ApplyMate workflow
    result = asyncio.run(run_applymate_job_agent())
    print("\n" + "="*60)
    print("APPLYMATE RESULTS:")
    print("="*60)
    if "error" not in result:
        print(f"✅ Jobs Found: {result['jobs_found']}")
        print(f"✅ Applications Submitted: {result['applied_count']}")
        print(f"📄 Resume Data: {result['resume_data']}")
        print(f"🎯 Preferences: {result['preferences']}")
    else:
        print(f"❌ Error: {result['error']}")
    print("="*60)
