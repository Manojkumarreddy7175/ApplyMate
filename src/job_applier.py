import os
import asyncio
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import logging
from bs4 import BeautifulSoup
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobApplier:
    def __init__(self):
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
                # Fallback to local chromedriver if available
                logger.warning(f"WebDriver manager failed: {driver_error}, trying local chromedriver")
                try:
                    self.driver = webdriver.Chrome(options=options)
                except Exception as local_error:
                    logger.error(f"Local chromedriver also failed: {local_error}")
                    raise Exception("Unable to initialize Chrome WebDriver. Please ensure Chrome is installed and chromedriver is available.")

            self.wait = WebDriverWait(self.driver, 10)
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
                "name": "Manoj Kumar reddy",
                "email": os.getenv('EMAIL_USER', 'john.doe@example.com'),
                "phone": "+9381483778",
                "address": "123 Main St, City, State 12345",
                "linkedin": "https://linkedin.com/in/manojkumarreddy7175",
                "website": "https://johndoe.com"
            }
            with open('personal_info.json', 'w') as f:
                json.dump(default_info, f)
            return default_info
        except json.JSONDecodeError:
            logger.error("Invalid JSON in personal_info.json")
            return {}

    def evaluate_job_relevance(self, job_data, cv_skills, preferences):
        """Evaluate job relevance based on CV skills and preferences."""
        score = 0
        description = job_data.get('description', '').lower()
        title = job_data.get('title', '').lower()

        # Check if required skills match
        for skill in cv_skills:
            if skill.lower() in description or skill.lower() in title:
                score += 1

        # Check salary requirements
        min_salary = preferences.get('min_salary', 0)
        salary_match = self.extract_salary_from_description(job_data.get('description', ''))
        if salary_match and salary_match >= min_salary:
            score += 1

        # Check location preference
        job_location = job_data.get('location', '').lower()
        pref_location = preferences.get('location', '').lower()
        if pref_location in job_location or 'remote' in job_location:
            score += 0.5

        # Minimum score threshold
        return score >= 2

    def extract_salary_from_description(self, description):
        """Extract salary information from job description."""
        import re
        salary_patterns = [
            r'\$([\d,]+(?:\.\d{2})?)',
            r'(\d{2,3})\s*k',
            r'salary[:\s].*?(\d{2,6})',
        ]
        for pattern in salary_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            for match in matches:
                try:
                    if 'k' in match.lower():
                        return int(match.replace('k', '').replace(',', '')) * 1000
                    else:
                        return int(match.replace(',', '').replace('$', ''))
                except ValueError:
                    continue
        return None

    def generate_cover_letter(self, job_data, cv_skills):
        """Generate a tailored cover letter based on job and CV."""
        company = job_data.get('company', 'the company')
        title = job_data.get('title', 'the position')
        skills_string = ', '.join(cv_skills[:3])

        cover_letter = f"""
Dear Hiring Manager,

I am writing to express my interest in the {title} position at {company}. With my expertise in {skills_string}, I am confident in my ability to contribute effectively to your team.

My background includes hands-on experience with the technologies mentioned in your job posting. I am particularly drawn to this opportunity because of {company}'s innovative approach and the chance to work on impactful projects.

I would welcome the opportunity to discuss how my skills and enthusiasm align with your needs. Thank you for considering my application.

Best regards,
[Your Name]
        """.strip()
        return cover_letter

    def apply_to_job_sync(self, job_data, cv_skills, preferences, resume_path):
        """Apply to a single job using browser automation (synchronous wrapper)."""
        try:
            url = job_data.get('link', '')
            if not url:
                logger.warning("No application URL provided")
                return False

            logger.info(f"Attempting to apply for job: {job_data.get('title', 'Unknown')} at {url}")

            # Navigate to application page
            self.driver.get(url)
            time.sleep(2)  # Wait for page load

            # Load personal info
            personal_info = self.load_personal_info()

            # Try different application strategies
            success = False

            # Strategy 1: Direct form submission (LinkedIn, etc.)
            if self._apply_linkedin_style(url, job_data, personal_info, resume_path):
                success = True

            # Strategy 2: Generic form filling
            elif self._apply_generic_form(url, job_data, personal_info, cv_skills, preferences, resume_path):
                success = True

            # Strategy 3: Greenhouse platform
            elif self._apply_greenhouse(url, job_data, personal_info, resume_path):
                success = True

            if success:
                logger.info(f"Successfully applied for job: {job_data.get('title', 'Unknown')}")
                # Wait a bit before next application to avoid rate limiting
                time.sleep(3)
                return True
            else:
                logger.warning(f"Could not apply to job: {job_data.get('title', 'Unknown')}")
                return False

        except Exception as e:
            logger.error(f"Error applying to job: {e}")
            return False
        finally:
            if self.driver:
                self.driver.delete_all_cookies()  # Clear session

    async def apply_to_job(self, job_data, cv_skills, preferences, resume_path):
        """Apply to a single job using browser automation."""
        return self.apply_to_job_sync(job_data, cv_skills, preferences, resume_path)

    def _apply_linkedin_style(self, url, job_data, personal_info, resume_path):
        """Apply on LinkedIn-style platforms."""
        try:
            if 'linkedin.com/jobs' not in url:
                return False

            # Click apply button (various possible selectors)
            apply_buttons = self.driver.find_elements(By.CSS_SELECTOR,
                "button[data-tracking-control-name='public_jobs_apply-button'], .jobs-apply-button, button[data-test-id='apply-button']"
            )

            if apply_buttons:
                apply_buttons[0].click()
                time.sleep(2)

                # Fill form fields
                self._fill_common_fields(personal_info, resume_path)
                return True
            return False
        except Exception as e:
            logger.error(f"LinkedIn apply failed: {e}")
            return False

    def _apply_greenhouse(self, url, job_data, personal_info, resume_path):
        """Apply on Greenhouse platforms."""
        try:
            if 'greenhouse.io' not in url:
                return False

            # Greenhouse uses iframes, need to switch context
            try:
                iframe = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
                self.driver.switch_to.frame(iframe)
            except:
                pass

            self._fill_common_fields(personal_info, resume_path)
            return True
        except Exception as e:
            logger.error(f"Greenhouse apply failed: {e}")
            return False

    def _apply_generic_form(self, url, job_data, personal_info, cv_skills, preferences, resume_path):
        """Apply using generic form filling strategy."""
        try:
            # Look for application forms
            forms = self.driver.find_elements(By.TAG_NAME, "form")

            if not forms:
                return False

            # Fill common fields in all forms
            self._fill_common_fields(personal_info, resume_path)

            # Generate cover letter
            cover_letter = self.generate_cover_letter(job_data, cv_skills)
            self._fill_cover_letter(cover_letter)

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

    def _fill_common_fields(self, personal_info, resume_path):
        """Fill common application form fields."""
        try:
            # First name, last name
            full_name = personal_info.get('name', 'John Doe').split(' ')
            first_name, last_name = full_name[0], ' '.join(full_name[1:]) if len(full_name) > 1 else 'Doe'

            self._fill_field("first_name, firstname, #first_name, #firstname, input[name*='first']", first_name)
            self._fill_field("last_name, lastname, #last_name, #lastname, input[name*='last']", last_name)

            # Email
            self._fill_field("email, #email, input[name*='email'], input[type='email']", personal_info.get('email', ''))

            # Phone
            self._fill_field("phone, #phone, input[name*='phone'], input[type='tel']", personal_info.get('phone', ''))

            # Resume upload
            self._upload_resume("file, resume, #resume, input[type='file'], input[accept*='pdf']", resume_path)

        except Exception as e:
            logger.error(f"Error filling common fields: {e}")

    def _fill_cover_letter(self, cover_letter):
        """Fill cover letter or additional info field."""
        try:
            self._fill_field("textarea, .cover-letter, #cover_letter, textarea[name*='cover']", cover_letter)
        except Exception as e:
            logger.error("Could not fill cover letter")

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

def apply_to_jobs(jobs_list, cv_skills, preferences, resume_path, max_applications=3):
    """Apply to top N relevant jobs."""
    applier = JobApplier()
    applied_count = 0

    try:
        for job in jobs_list[:max_applications]:
            if applier.evaluate_job_relevance(job, cv_skills, preferences):
                try:
                    success = applier.apply_to_job_sync(job, cv_skills, preferences, resume_path)
                    if success:
                        applied_count += 1
                        logger.info(f"Applied to job #{applied_count}")
                except Exception as e:
                    logger.error(f"Failed to apply to job: {e}")
    finally:
        applier.close()

    return applied_count
