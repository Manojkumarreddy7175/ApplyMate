"""
Stagehand MCP Browser Automation Integration
Uses Stagehand MCP server for natural language browser automation
"""

import asyncio
import os
import logging
from typing import Dict, List, Optional
from mcp_use import MCPClient, MCPAgent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StagehandAutomation:
    """Natural language browser automation using Stagehand MCP"""
    
    def __init__(self):
        self.client = None
        self.agent = None
        
    async def initialize(self):
        """Initialize Stagehand MCP connection"""
        self.client = MCPClient.from_config_file("config/mcp_config.json")
        
        os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.1
        )
        
        self.agent = MCPAgent(llm=llm, client=self.client, max_steps=50, verbose=True)
        logger.info("✅ Stagehand MCP initialized")
    
    async def apply_to_job(self, job: Dict, personal_info: Dict, resume_path: str) -> Dict:
        """
        Apply to a job using natural language browser automation
        
        Args:
            job: Job details (title, company, link, etc.)
            personal_info: User personal information
            resume_path: Path to resume file
            
        Returns:
            Dict with success status and details
        """
        job_url = job.get('link', '')
        if not job_url:
            return {'success': False, 'error': 'No job URL provided'}
        
        logger.info(f"🚀 Applying to: {job.get('title')} at {job.get('company')}")
        
        prompt = f"""
        You are a job application assistant. Use the browser automation tool to apply for this job.
        
        Job Details:
        - Title: {job.get('title')}
        - Company: {job.get('company')}
        - URL: {job_url}
        
        Applicant Information:
        - Name: {personal_info.get('name')}
        - Email: {personal_info.get('email')}
        - Phone: {personal_info.get('phone')}
        - LinkedIn: {personal_info.get('linkedin', 'N/A')}
        
        Resume: {resume_path}
        
        TASK: Navigate to the job URL and complete the application:
        
        1. Go to {job_url}
        2. Find and click the "Apply" button (may say "Apply Now", "Easy Apply", "Submit Application")
        3. Fill out the application form:
           - Full Name: {personal_info.get('name')}
           - Email: {personal_info.get('email')}
           - Phone: {personal_info.get('phone')}
           - LinkedIn: {personal_info.get('linkedin', '')}
           - Upload resume if there's a file upload field
        4. If there's a cover letter field, use: {personal_info.get('cover_letter_template', 'I am excited to apply for this position.')}
        5. Answer any standard questions (years of experience, willing to relocate, etc.) intelligently
        6. DO NOT click final submit - stop at the review page
        7. Take a screenshot of the filled form
        8. Return the status
        
        Report back:
        - Whether you successfully filled the form
        - Any errors encountered
        - What fields were filled
        """
        
        try:
            result = await self.agent.run(prompt)
            
            # Parse result
            success = 'success' in result.lower() and 'error' not in result.lower()
            
            return {
                'success': success,
                'job_title': job.get('title'),
                'company': job.get('company'),
                'url': job_url,
                'details': result
            }
            
        except Exception as e:
            logger.error(f"❌ Application failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'job_title': job.get('title'),
                'company': job.get('company')
            }
    
    async def extract_job_details(self, job_url: str) -> Dict:
        """
        Extract detailed job information from a job posting URL
        
        Args:
            job_url: URL of the job posting
            
        Returns:
            Dict with extracted job details
        """
        prompt = f"""
        Navigate to {job_url} and extract all relevant job information.
        
        Extract:
        - Job title
        - Company name
        - Location (remote/hybrid/onsite)
        - Salary range (if mentioned)
        - Required skills
        - Job description (first 500 characters)
        - Application deadline (if mentioned)
        - Job type (Full-time, Internship, Contract, etc.)
        
        Return as JSON format.
        """
        
        try:
            result = await self.agent.run(prompt)
            return {'success': True, 'data': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def batch_apply(self, jobs: List[Dict], personal_info: Dict, resume_path: str, max_applications: int = 5):
        """
        Apply to multiple jobs in batch
        
        Args:
            jobs: List of job dictionaries
            personal_info: User personal information
            resume_path: Path to resume
            max_applications: Maximum number of applications to send
        """
        results = []
        
        for i, job in enumerate(jobs[:max_applications]):
            logger.info(f"\n📝 Application {i+1}/{min(len(jobs), max_applications)}")
            
            result = await self.apply_to_job(job, personal_info, resume_path)
            results.append(result)
            
            # Wait between applications
            if i < len(jobs) - 1:
                logger.info("⏳ Waiting 30 seconds before next application...")
                await asyncio.sleep(30)
        
        # Summary
        successful = sum(1 for r in results if r.get('success'))
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ Successfully applied: {successful}/{len(results)}")
        logger.info(f"❌ Failed: {len(results) - successful}")
        logger.info(f"{'='*60}")
        
        return results
    
    async def close(self):
        """Close MCP connections"""
        if self.client:
            await self.client.close_all_sessions()


# Example usage
async def main():
    automation = StagehandAutomation()
    await automation.initialize()
    
    # Test with sample job
    job = {
        'title': 'AI Engineer Intern',
        'company': 'Test Company',
        'link': 'https://example.com/job/123'
    }
    
    personal_info = {
        'name': 'John Doe',
        'email': 'john@example.com',
        'phone': '+1-234-567-8900',
        'linkedin': 'https://linkedin.com/in/johndoe'
    }
    
    result = await automation.apply_to_job(job, personal_info, 'temp_resume.pdf')
    print(result)
    
    await automation.close()


if __name__ == "__main__":
    asyncio.run(main())
