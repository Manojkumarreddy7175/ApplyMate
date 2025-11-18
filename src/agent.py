import asyncio
import json
import os
import pandas as pd
import re
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from mcp_use import MCPAgent, MCPClient, set_debug
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
from enhanced_job_platforms import JobPlatformManager, JobPlatform
from enhanced_job_applier import EnhancedJobApplier
from job_applier import apply_to_jobs
from resume_parser import parse_resume
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_agent_result(agent_result):
    """
    Parse the agent result to extract jobs data and application status.
    Returns: (jobs_list, number_applied)
    """
    jobs_list = []
    number_applied = 0

    # Try to extract JSON data from the result
    try:
        # Look for JSON patterns in the result
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

    # If no JSON found, try manual parsing from the text
    if not jobs_list:
        # Extract jobs information from the text response
        lines = agent_result.split('\n')
        current_job = {}

        for line in lines:
            line = line.strip()
            if 'title:' in line.lower() or line.startswith('- '):
                # Save previous job if exists
                if current_job and len(current_job) >= 3:  # minimum required fields
                    jobs_list.append(current_job)
                current_job = {}

                # Extract title
                title_match = re.search(r'title:?\s*(.+)', line, re.IGNORECASE)
                if title_match:
                    current_job['title'] = title_match.group(1).strip()
                else:
                    current_job['title'] = line.replace('- ', '').strip()

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
                    # Consider this job complete
                    if len(current_job) >= 3:
                        jobs_list.append(current_job)
                        current_job = {}

            elif 'applied' in line.lower() and 'success' in line.lower():
                number_applied += 1

        # Add the last job if exists
        if current_job and len(current_job) >= 3:
            jobs_list.append(current_job)

    # Extract number of applications from text
    applied_match = re.search(r'applied to (\d+)', agent_result, re.IGNORECASE)
    if applied_match:
        number_applied = int(applied_match.group(1))

    # Fill in missing fields with defaults
    for job in jobs_list:
        if 'title' not in job:
            job['title'] = 'Unknown Position'
        if 'company' not in job:
            job['company'] = 'Unknown Company'
        if 'location' not in job:
            job['location'] = 'Remote'
        if 'link' not in job:
            job['link'] = ''
        if 'description' not in job:
            job['description'] = ''
        if 'salary' not in job:
            # Try to extract salary from description
            salary_match = re.search(r'\$[\d,]+(?:k|-[\d,]+k?)', job.get('description', ''), re.IGNORECASE)
            if salary_match:
                job['salary'] = salary_match.group()
            else:
                job['salary'] = 'Not specified'

    return jobs_list, number_applied

def evaluate_job_relevance(job_data, cv_skills, preferences):
    """Evaluate job relevance based on CV skills and preferences."""
    score = 0
    description = job_data.get('description', '').lower()
    title = job_data.get('title', '').lower()
    company = job_data.get('company', '').lower()

    # Check if required skills match (higher weight)
    for skill in cv_skills[:15]:  # Top 15 skills
        if skill.lower() in description or skill.lower() in title:
            score += 1.5

    # Check focus areas
    focus_areas = preferences.get('focus_areas', [])
    for area in focus_areas:
        if area.lower() in description or area.lower() in title:
            score += 2  # Higher weight for focus areas
    
    # Check if it's an internship/entry-level position (important for this profile)
    internship_keywords = ['intern', 'internship', 'entry-level', 'junior', 'graduate', 'trainee']
    if any(keyword in title or keyword in description for keyword in internship_keywords):
        score += 2

    # Check preferred companies
    preferred_companies = preferences.get('preferred_companies', [])
    for pref_company in preferred_companies:
        if pref_company.lower() in company:
            score += 3  # High bonus for preferred companies

    # Check location preference
    job_location = job_data.get('location', '').lower()
    all_locations = preferences.get('all_locations', [preferences.get('location', 'Remote')])
    if any(loc.lower() in job_location for loc in all_locations):
        score += 1
    if 'remote' in job_location or 'hybrid' in job_location:
        score += 1

    # Check salary requirements if specified (less important for internships)
    min_salary = preferences.get('min_salary', 0)
    if min_salary > 0:
        salary_text = job_data.get('salary', '').lower()
        if salary_text and salary_text != 'not specified':
            if 'k' in salary_text or '$' in salary_text:
                try:
                    salary_num = int(re.findall(r'\d+', salary_text)[0])
                    if 'k' in salary_text:
                        salary_num *= 1000
                    if salary_num >= min_salary:
                        score += 1
                except:
                    pass

    # Minimum score threshold - need at least 3 points
    return score >= 3

load_dotenv()
set_debug(2)

async def parse_resume(resume_path):
    client = MCPClient.from_config_file("mcp_config.json")
    os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.1
    )
    agent = MCPAgent(llm=llm, client=client, max_steps=50, verbose=True)
    
    prompt = f"Parse the resume at {resume_path} and extract the following information as JSON: current role, preferred role, location, skills, minimum salary expectation."
    result = await agent.run(prompt)
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        return {}

async def collect_preferences(resume_data):
    # Load existing preferences (if any)
    try:
        with open('preferences.json', 'r') as f:
            prefs = json.load(f)
    except FileNotFoundError:
        prefs = {}
    
    # Extract data from comprehensive preferences structure
    if "ideal_positions" in prefs:
        # New comprehensive format
        primary_position = prefs["ideal_positions"][0]  # Use first position as primary
        
        # Collect all skills from all positions
        all_skills = []
        for position in prefs["ideal_positions"]:
            all_skills.extend(position.get("preferred_languages", []))
            all_skills.extend(position.get("tools_frameworks", []))
        
        # Remove duplicates while preserving order
        unique_skills = list(dict.fromkeys(all_skills))
        
        # Get all location preferences
        locations = prefs.get("work_preferences", {}).get("location", ["Remote"])
        
        merged_prefs = {
            "profile_owner": prefs.get("profile_owner", ""),
            "title": primary_position.get("title", "AI Engineer Intern"),
            "all_titles": [pos["title"] for pos in prefs["ideal_positions"]],
            "location": locations[0] if locations else "Remote",  # Primary location
            "all_locations": locations,
            "skills": unique_skills[:20],  # Top 20 skills
            "focus_areas": primary_position.get("focus_areas", []),
            "min_salary": 0,  # Intern positions typically don't specify minimum salary
            "preferred_companies": [
                comp for company_type in prefs.get("ideal_company_types", [])
                for comp in company_type.get("example_companies", [])
            ],
            "career_goals": prefs.get("work_preferences", {}).get("career_goals", [])
        }
    else:
        # Old simple format or resume data
        merged_prefs = {
            "title": resume_data.get("preferred role", prefs.get("title", "Software Engineer")),
            "location": resume_data.get("location", prefs.get("location", "Remote")),
            "skills": resume_data.get("skills", prefs.get("skills", ["Python", "AI"])),
            "min_salary": resume_data.get("minimum salary expectation", prefs.get("min_salary", 0))
        }
    
    return merged_prefs

async def run_job_agent(resume_path="temp_resume.pdf"):
    # Parse resume using new parser
    from resume_parser import parse_resume as real_parse_resume
    resume_data = await real_parse_resume(resume_path)

    # Collect preferences (interactive via Streamlit or here)
    prefs = await collect_preferences(resume_data)

    client = MCPClient.from_config_file("mcp_config.json")

    os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.1
    )
    
    agent = MCPAgent(llm=llm, client=client, max_steps=100, verbose=True)
    
    # Build search query based on multiple positions
    all_titles = prefs.get('all_titles', [prefs['title']])
    title_query = ' OR '.join(all_titles[:3])  # Top 3 positions
    
    # Key skills for search
    key_skills = prefs.get('skills', [])[:5]
    skills_query = ' '.join(key_skills)
    
    # Location preferences
    location_query = ' OR '.join(prefs.get('all_locations', [prefs['location']]))
    
    prompt = f"""
    You are an automated job agent for {prefs.get('profile_owner', 'User')}.

    Profile:
    - Seeking: {title_query}
    - Key Skills: {', '.join(key_skills)}
    - Focus Areas: {', '.join(prefs.get('focus_areas', [])[:3])}
    - Location: {location_query}
    
    TASK: Search for internship/entry-level job listings and return them in JSON format.

    1. Use firecrawl_search with:
       - query: "({title_query}) internship ({location_query}) {skills_query}"
       - limit: 15
       - sources: [{{"type": "web"}}]

    2. FROM SEARCH RESULTS: Extract and return job info as valid JSON array:
       ```json
       [
         {{
           "title": "Job Title from search result",
           "company": "Extract company name from description or title",
           "location": "Extract location or use '{prefs['location']}'",
           "link": "URL from search result",
           "description": "Description from search result (first 300 chars)",
           "salary": "Extract salary if mentioned, otherwise 'Not specified'",
           "job_type": "Internship/Entry-level/Full-time"
         }}
       ]
       ```

    3. FILTER: Keep jobs matching these criteria:
       - Contains keywords: {', '.join(key_skills[:8])}
       - Job type: Internship, Entry-level, or Junior positions
       - Relevant to: {', '.join(prefs.get('focus_areas', [])[:3])}
       
    4. PRIORITIZE companies: {', '.join(prefs.get('preferred_companies', [])[:10])}

    IMPORTANT: Return ONLY the JSON array, no other text. Do not simulate saving to CSV or sending emails - just return the data.
    """
    
    try:
        result = await agent.run(prompt)
        jobs_data, number_applied = parse_agent_result(result)

        # Filter jobs for relevance
        cv_skills = prefs['skills']
        filtered_jobs = [job for job in jobs_data if evaluate_job_relevance(job, cv_skills, prefs)]

        df = pd.DataFrame(filtered_jobs, columns=['title', 'company', 'location', 'link', 'description', 'salary'])
        df.to_csv('jobs_dashboard.csv', index=False)
        print(f"Dashboard CSV saved: {len(filtered_jobs)} jobs found")

        # Auto-apply to top jobs
        applied_status = 0
        if filtered_jobs:
            try:
                applied_status = apply_to_jobs(filtered_jobs, cv_skills, prefs, resume_path, max_applications=3)
                print(f"Auto-applied to {applied_status} jobs")
            except Exception as e:
                print(f"Application failed: {e}")
                applied_status = 0

        try:
            send_email_alert(df, result)
        except Exception as e:
            print(f"Email sending failed: {e}")

        return f"Found {len(filtered_jobs)} jobs, applied to {applied_status}"
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return str(e)
    finally:
        await client.close_all_sessions()

def send_email_alert(df, result):
    sender = os.getenv('EMAIL_USER')
    password = os.getenv('EMAIL_PASS')
    msg = MIMEMultipart('alternative')
    msg['From'] = sender
    msg['To'] = sender
    
    if len(df) > 0:
        msg['Subject'] = f"{len(df)} New Job Matches!"
        html = f"<h2>New Jobs!</h2>{df[['title', 'company', 'location', 'link']].to_html(index=False)}"
    else:
        msg['Subject'] = "Application Errors or No Matches"
        html = f"<h2>Issues Encountered</h2><p>Details: {result}</p>"
    
    msg.attach(MIMEText(html, 'html'))
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
        server.login(sender, password)
        server.sendmail(sender, sender, msg.as_string())
    print("Email alert sent!")

if __name__ == "__main__":
    asyncio.run(run_job_agent())
