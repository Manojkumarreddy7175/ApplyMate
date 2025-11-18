"""
Enhanced Scheduled Job Automation
Automatically searches for jobs and applies via browser automation at scheduled times.

This replaces mail_watcher.py with pure time-based automation.
Runs browser automation at configured times to:
1. Search for matching jobs
2. Filter by preferences
3. Auto-apply using Selenium (fills all form details)
4. Save results to CSV
5. Send email notification

Configuration:
- Schedule times via environment variables or config
- All application details from personal_info.json
- Job preferences from preferences.json
"""

import asyncio
import os
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
import pandas as pd

from enhanced_job_applier import EnhancedJobApplier
from enhanced_job_platforms import JobPlatformManager
from agent import run_job_agent, send_email_alert, collect_preferences
from resume_parser import parse_resume

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ScheduledJobAutomation:
    """Manages scheduled job search and application automation"""
    
    def __init__(self, resume_path: str = "temp_resume.pdf"):
        self.resume_path = resume_path
        self.scheduler = BackgroundScheduler()
        
        # Load configuration
        self.schedule_times = self._load_schedule_config()
        self.max_applications = int(os.getenv('MAX_APPLICATIONS_PER_RUN', '5'))
        
    def _load_schedule_config(self):
        """Load scheduling configuration from environment"""
        # Default: Run at 9 AM and 6 PM on weekdays
        default_schedules = [
            {'hour': 9, 'minute': 0, 'day_of_week': 'mon-fri'},
            {'hour': 18, 'minute': 0, 'day_of_week': 'mon-fri'}
        ]
        
        # You can override via environment variables
        custom_hour = os.getenv('SCHEDULE_HOUR')
        if custom_hour:
            try:
                hour = int(custom_hour)
                minute = int(os.getenv('SCHEDULE_MINUTE', '0'))
                days = os.getenv('SCHEDULE_DAYS', 'mon-fri')
                return [{'hour': hour, 'minute': minute, 'day_of_week': days}]
            except ValueError:
                logger.warning("Invalid schedule configuration, using defaults")
        
        return default_schedules
    
    async def run_automated_job_search_and_apply(self):
        """Main automation function - searches and applies to jobs"""
        logger.info(f"\n{'='*60}")
        logger.info(f"🤖 SCHEDULED JOB AUTOMATION STARTED")
        logger.info(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"{'='*60}\n")
        
        try:
            # Step 1: Use the existing agent to search and get jobs
            logger.info("🤖 Step 1: Running job search agent...")
            
            # Run the agent which handles search and filtering
            from agent import run_job_agent
            agent_result = await run_job_agent(self.resume_path)
            
            logger.info(f"✅ Agent completed: {agent_result}")
            
            # Load the jobs from CSV (agent saves them there)
            try:
                df = pd.read_csv('jobs_dashboard.csv')
                all_jobs = df.to_dict('records')
                logger.info(f"✅ Loaded {len(all_jobs)} jobs from agent results")
            except Exception as e:
                logger.warning(f"⚠️ Could not load jobs from CSV: {e}")
                all_jobs = []
            
            # Get preferences for filtering
            resume_data = await parse_resume(self.resume_path)
            prefs = await collect_preferences(resume_data)
            logger.info(f"✅ Preferences: {prefs.get('title', 'Unknown')} in {prefs.get('location', 'Unknown')}")
            
            # Step 2: Filter jobs based on preferences (agent already filters, but we can refine)
            logger.info(f"\n🎯 Step 2: Refining job matches...")
            filtered_jobs = self._filter_jobs(all_jobs, prefs) if all_jobs else []
            logger.info(f"✅ Final selection: {len(filtered_jobs)} jobs to apply")
            
            # Jobs already saved by agent, update if we refined
            if filtered_jobs and filtered_jobs != all_jobs:
                df = pd.DataFrame(filtered_jobs)
                df.to_csv('jobs_dashboard_filtered.csv', index=False)
                logger.info(f"💾 Saved {len(filtered_jobs)} refined jobs to jobs_dashboard_filtered.csv")
            
            # Step 3: Auto-apply to top jobs
            if not filtered_jobs:
                logger.warning("⚠️ No jobs found matching criteria")
                return {
                    'jobs_found': 0,
                    'applications_sent': 0,
                    'success_rate': 0
                }
            
            logger.info(f"\n🚀 Step 3: Auto-applying to top {min(len(filtered_jobs), self.max_applications)} jobs...")
            
            applier = EnhancedJobApplier(resume_path=self.resume_path)
            
            try:
                results = applier.apply_to_multiple_jobs(
                    jobs=filtered_jobs,
                    max_applications=self.max_applications,
                    delay_between_apps=15  # 15 seconds between applications
                )
                
                logger.info(f"\n{'='*60}")
                logger.info(f"📊 AUTOMATION RESULTS")
                logger.info(f"{'='*60}")
                logger.info(f"🔍 Jobs Found: {len(all_jobs)}")
                logger.info(f"✅ Jobs Matching Criteria: {len(filtered_jobs)}")
                logger.info(f"📤 Applications Sent: {results['successful']}")
                logger.info(f"❌ Applications Failed: {results['failed']}")
                logger.info(f"📈 Success Rate: {(results['successful'] / max(1, results['total_attempted'])) * 100:.1f}%")
                logger.info(f"{'='*60}\n")
                
                # Step 4: Send email notification
                try:
                    logger.info("📧 Step 4: Sending email notification...")
                    df = pd.DataFrame(filtered_jobs[:10])  # Top 10 for email
                    summary = f"Applied to {results['successful']}/{results['total_attempted']} jobs"
                    send_email_alert(df, summary)
                    logger.info("✅ Email notification sent")
                except Exception as e:
                    logger.error(f"❌ Email notification failed: {e}")
                
                return {
                    'jobs_found': len(all_jobs),
                    'jobs_filtered': len(filtered_jobs),
                    'applications_sent': results['successful'],
                    'applications_failed': results['failed'],
                    'success_rate': (results['successful'] / max(1, results['total_attempted'])) * 100
                }
                
            finally:
                applier.close()
        
        except Exception as e:
            logger.exception(f"❌ Automation failed: {e}")
            return {
                'jobs_found': 0,
                'applications_sent': 0,
                'error': str(e)
            }
    
    def _filter_jobs(self, jobs, preferences):
        """Filter jobs based on comprehensive user preferences"""
        filtered = []
        
        required_skills = [skill.lower() for skill in preferences.get('skills', [])]
        all_locations = [loc.lower() for loc in preferences.get('all_locations', [preferences.get('location', 'Remote')])]
        focus_areas = [area.lower() for area in preferences.get('focus_areas', [])]
        preferred_companies = [comp.lower() for comp in preferences.get('preferred_companies', [])]
        min_salary = preferences.get('min_salary', 0)
        
        for job in jobs:
            score = 0
            description = job.get('description', '').lower()
            title = job.get('title', '').lower()
            location = job.get('location', '').lower()
            company = job.get('company', '').lower()
            
            # Check skills (high priority)
            matching_skills = sum(1 for skill in required_skills[:15] if skill in description or skill in title)
            score += matching_skills * 1.5
            
            # Check focus areas (very high priority)
            matching_focus = sum(1 for area in focus_areas if area in description or area in title)
            score += matching_focus * 2
            
            # Check if internship/entry-level (important for this profile)
            internship_keywords = ['intern', 'internship', 'entry-level', 'junior', 'graduate', 'trainee']
            if any(keyword in title or keyword in description for keyword in internship_keywords):
                score += 2
            
            # Check preferred companies (high bonus)
            if any(pref_comp in company for pref_comp in preferred_companies):
                score += 3
            
            # Check location
            if any(loc in location for loc in all_locations):
                score += 1
            if 'remote' in location or 'hybrid' in location or 'work from home' in description:
                score += 1
            
            # Check salary (less important for internships)
            if min_salary > 0:
                salary_str = job.get('salary', '').lower()
                if salary_str and 'not specified' not in salary_str:
                    score += 0.5
            
            # Must have at least 3 points to be considered (higher threshold for quality)
            if score >= 3:
                job['relevance_score'] = score
                filtered.append(job)
        
        # Sort by relevance score (highest first)
        filtered.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return filtered
    
    def schedule_job(self):
        """Add scheduled jobs to the scheduler"""
        for schedule in self.schedule_times:
            trigger = CronTrigger(
                hour=schedule['hour'],
                minute=schedule['minute'],
                day_of_week=schedule['day_of_week']
            )
            
            self.scheduler.add_job(
                lambda: asyncio.run(self.run_automated_job_search_and_apply()),
                trigger=trigger,
                id=f"job_automation_{schedule['hour']}_{schedule['minute']}",
                name=f"Job Automation at {schedule['hour']}:{schedule['minute']:02d}",
                replace_existing=True
            )
            
            logger.info(f"✅ Scheduled: Job automation at {schedule['hour']}:{schedule['minute']:02d} on {schedule['day_of_week']}")
    
    def run_now(self):
        """Run the automation immediately (for testing)"""
        logger.info("🚀 Running automation NOW (manual trigger)...")
        result = asyncio.run(self.run_automated_job_search_and_apply())
        return result
    
    def start(self):
        """Start the scheduler"""
        self.schedule_job()
        self.scheduler.start()
        
        logger.info(f"\n{'='*60}")
        logger.info("🤖 SCHEDULED JOB AUTOMATION ACTIVE")
        logger.info(f"{'='*60}")
        logger.info(f"📅 Schedule:")
        for schedule in self.schedule_times:
            logger.info(f"   - {schedule['hour']}:{schedule['minute']:02d} on {schedule['day_of_week']}")
        logger.info(f"📊 Max applications per run: {self.max_applications}")
        logger.info(f"📄 Resume: {self.resume_path}")
        logger.info(f"{'='*60}")
        logger.info("👀 Waiting for scheduled times... (Press Ctrl+C to stop)\n")
        
        try:
            # Keep the script running
            import time
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("\n🛑 Scheduler stopped by user")
            self.scheduler.shutdown()
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("🛑 Scheduler stopped")


def main():
    """Main entry point"""
    import sys
    
    resume_path = os.getenv('RESUME_PATH', 'temp_resume.pdf')
    
    # Check if resume exists
    if not os.path.exists(resume_path):
        logger.error(f"❌ Resume file not found: {resume_path}")
        logger.error("Please set RESUME_PATH in .env or create temp_resume.pdf")
        return 1
    
    automation = ScheduledJobAutomation(resume_path=resume_path)
    
    # Check for command-line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == 'now':
            # Run immediately
            logger.info("Running automation NOW (one-time)...")
            result = automation.run_now()
            logger.info(f"\n✅ Automation complete: {result}")
            return 0
        elif sys.argv[1] == 'test':
            # Test configuration
            logger.info("Testing configuration...")
            logger.info(f"Resume: {resume_path}")
            logger.info(f"Schedule times: {automation.schedule_times}")
            logger.info(f"Max applications: {automation.max_applications}")
            return 0
    
    # Start scheduler
    automation.start()
    return 0


if __name__ == '__main__':
    exit(main())
