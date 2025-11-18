#!/usr/bin/env python3
"""
Pure Selenium Job Application Script
Standalone script for automated job applications using Selenium WebDriver
"""
import os
import json
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JobApplicationBot:
    def __init__(self, resume_path="temp_resume.pdf"):
        self.resume_path = resume_path
        self.driver = None
        self.wait = None
        self.initialize_driver()

    def initialize_driver(self):
        """Initialize Selenium WebDriver with Chrome."""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")  # Run in headless mode
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-images")
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

            # Try webdriver manager first
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
            except Exception as driver_error:
                logger.warning(f"WebDriver manager failed: {driver_error}, trying local chromedriver")
                try:
                    self.driver = webdriver.Chrome(options=options)
                except Exception as local_error:
                    logger.error(f"Local chromedriver also failed: {local_error}")
                    raise Exception("Unable to initialize Chrome WebDriver. Please ensure Chrome is installed.")

            self.wait = WebDriverWait(self.driver, 15)
            logger.info("Chrome driver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            raise

    def load_personal_info(self):
        """Load personal information for applications."""
        try:
            with open('personal_info.example.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("personal_info.example.json not found, creating default info")
            # Create default info if file doesn't exist
            default_info = {
                "name": "Manoj Kumar Reddy Koduru",
                "email": os.getenv('EMAIL_USER', 'manojkumarreddy7175@gmail.com'),
                "phone": "+91 9381483778",
                "address": "Kadapa, Andhra Pradesh, India",
                "linkedin": "https://linkedin.com/in/manojkumarreddy7175/",
                "website": "https://github.com/Manojkumarreddy7175"
            }
            with open('personal_info.json', 'w') as f:
                json.dump(default_info, f)
            return default_info
        except json.JSONDecodeError:
            logger.error("Invalid JSON in personal_info.json")
            return {}

    def apply_to_job_url(self, job_url):
        """Apply to a single job URL."""
        try:
            logger.info(f"Navigating to job URL: {job_url}")
            self.driver.get(job_url)
            time.sleep(3)  # Wait for page load

            # Load personal info
            personal_info = self.load_personal_info()

            # Try different application strategies based on the site
            success = False

            # Strategy 1: Naukri.com
            if 'naukri.com' in job_url:
                success = self._apply_naukri(job_url, personal_info)

            # Strategy 2: Indeed.com
            elif 'indeed.com' in job_url:
                success = self._apply_indeed(job_url, personal_info)

            # Strategy 3: LinkedIn
            elif 'linkedin.com' in job_url:
                success = self._apply_linkedin(job_url, personal_info)

            # Strategy 4: Generic form filling
            else:
                success = self._apply_generic_form(job_url, personal_info)

            if success:
                logger.info(f"✅ Successfully applied to: {job_url}")
                return True
            else:
                logger.warning(f"❌ Could not apply to: {job_url}")
                return False

        except Exception as e:
            logger.error(f"Error applying to {job_url}: {e}")
            return False
        finally:
            # Clear cookies for next application
            if self.driver:
                self.driver.delete_all_cookies()

    def _apply_naukri(self, url, personal_info):
        """Apply on Naukri.com"""
        try:
            # Naukri.com specific selectors
            apply_buttons = self.driver.find_elements(By.CSS_SELECTOR,
                "button[data-ga-track='FF_Tracking|Belly_SRP'], .btn14, .apply-button"
            )

            if apply_buttons:
                apply_buttons[0].click()
                time.sleep(3)

                # Fill common fields
                self._fill_common_fields(personal_info)
                return True
            return False
        except Exception as e:
            logger.error(f"Naukri apply failed: {e}")
            return False

    def _apply_indeed(self, url, personal_info):
        """Apply on Indeed.com"""
        try:
            # Indeed specific selectors
            apply_buttons = self.driver.find_elements(By.CSS_SELECTOR,
                "button[title*='Apply'], .jobsearch-IndeedApplyButton, .apply-button"
            )

            if apply_buttons:
                apply_buttons[0].click()
                time.sleep(3)

                # Fill common fields
                self._fill_common_fields(personal_info)
                return True
            return False
        except Exception as e:
            logger.error(f"Indeed apply failed: {e}")
            return False

    def _apply_linkedin(self, url, personal_info):
        """Apply on LinkedIn"""
        try:
            # LinkedIn specific selectors
            apply_buttons = self.driver.find_elements(By.CSS_SELECTOR,
                "button[data-tracking-control-name='public_jobs_apply-button'], .jobs-apply-button"
            )

            if apply_buttons:
                apply_buttons[0].click()
                time.sleep(3)

                # Fill common fields
                self._fill_common_fields(personal_info)
                return True
            return False
        except Exception as e:
            logger.error(f"LinkedIn apply failed: {e}")
            return False

    def _apply_generic_form(self, url, personal_info):
        """Apply using generic form filling strategy."""
        try:
            # Look for application forms
            forms = self.driver.find_elements(By.TAG_NAME, "form")

            if not forms:
                return False

            # Fill common fields in all forms
            self._fill_common_fields(personal_info)

            # Try to submit the form
            submit_buttons = self.driver.find_elements(By.CSS_SELECTOR,
                "input[type='submit'], button[type='submit'], .submit-button, .apply-button"
            )

            if submit_buttons:
                # Scroll to submit button
                self.driver.execute_script("arguments[0].scrollIntoView();", submit_buttons[0])
                submit_buttons[0].click()
                time.sleep(3)
                return True
            return False
        except Exception as e:
            logger.error(f"Generic form apply failed: {e}")
            return False

    def _fill_common_fields(self, personal_info):
        """Fill common application form fields."""
        try:
            # First name, last name
            full_name = personal_info.get('name', 'Manoj Kumar Reddy Koduru').split(' ')
            first_name, last_name = full_name[0], ' '.join(full_name[1:]) if len(full_name) > 1 else 'Koduru'

            self._fill_field("first_name, firstname, #first_name, #firstname, input[name*='first']", first_name)
            self._fill_field("last_name, lastname, #last_name, #lastname, input[name*='last']", last_name)

            # Email
            self._fill_field("email, #email, input[name*='email'], input[type='email']", personal_info.get('email', ''))

            # Phone
            self._fill_field("phone, #phone, input[name*='phone'], input[type='tel']", personal_info.get('phone', ''))

            # Resume upload
            self._upload_resume("file, resume, #resume, input[type='file'], input[accept*='pdf']", self.resume_path)

        except Exception as e:
            logger.error(f"Error filling common fields: {e}")

    def _fill_field(self, selector_string, value):
        """Fill a form field given multiple possible selectors."""
        selectors = selector_string.split(', ')
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed():
                        element.clear()
                        element.send_keys(value)
                        logger.info(f"Filled field {selector} with {value[:20]}...")
                        return True
            except:
                continue
        return False

    def _upload_resume(self, selector_string, resume_path):
        """Upload resume file given multiple possible selectors."""
        selectors = selector_string.split(', ')
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed():
                        element.send_keys(os.path.abspath(resume_path))
                        logger.info("Resume uploaded successfully")
                        time.sleep(2)  # Wait for upload
                        return True
            except Exception as e:
                logger.error(f"Resume upload failed: {e}")
                continue
        return False

    def close(self):
        """Close the browser driver."""
        if self.driver:
            self.driver.quit()
            logger.info("Browser driver closed")

def run_job_applications(job_urls, resume_path="temp_resume.pdf"):
    """Run job applications on a list of URLs."""
    bot = JobApplicationBot(resume_path)
    results = {"successful": 0, "failed": 0, "total": len(job_urls)}

    try:
        logger.info(f"Starting job applications for {len(job_urls)} URLs")

        for i, url in enumerate(job_urls, 1):
            logger.info(f"Processing job {i}/{len(job_urls)}: {url}")
            try:
                success = bot.apply_to_job_url(url)
                if success:
                    results["successful"] += 1
                else:
                    results["failed"] += 1
            except Exception as e:
                logger.error(f"Failed to process {url}: {e}")
                results["failed"] += 1

            # Wait between applications to avoid rate limiting
            time.sleep(5)

    finally:
        bot.close()

    return results

if __name__ == "__main__":
    # Example usage with sample job URLs
    sample_job_urls = [
        "https://www.naukri.com/java-and-python-jobs",
        "https://www.naukri.com/sql-python-jobs",
        "https://in.indeed.com/q-python-java-sql-fresher-jobs.html",
        "https://in.linkedin.com/jobs/software-developer-java-python-sql-jobs"
    ]

    print("🚀 Starting Pure Selenium Job Application Bot")
    print("=" * 60)

    results = run_job_applications(sample_job_urls, "manoj_resume.txt")

    print("\n" + "=" * 60)
    print("FINAL RESULTS:")
    print("=" * 60)
    print(f"✅ Successful Applications: {results['successful']}")
    print(f"❌ Failed Applications: {results['failed']}")
    print(f"📊 Total Processed: {results['total']}")
    print(f"🎯 Success Rate: {results['successful']/results['total']*100:.1f}%")
    print("=" * 60)
