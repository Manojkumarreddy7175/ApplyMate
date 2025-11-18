from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
import sys
import os
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent import run_job_agent

async def scheduled_run():
    print(f"[{datetime.now()}] Starting Scheduled MCP Agent Run...")
    await run_job_agent(resume_path="temp_resume.pdf")
    print("Scheduled Run Complete!")

def main():
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: asyncio.run(scheduled_run()), 'cron', hour=9, day_of_week='mon-fri')
    scheduler.start()
    print("Scheduler started. Agent will run automatically. Press Ctrl+C to stop.")
    try:
        while True:
            import time
            time.sleep(60)
    except KeyboardInterrupt:
        scheduler.shutdown()

if __name__ == "__main__":
    main()