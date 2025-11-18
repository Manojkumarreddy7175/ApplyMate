"""
Enhanced Job Applier Module
Improved reliability, error handling, and multi-platform application support
"""

import os
import time
import random
import logging
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ApplicationResult:
    """Result of a job application attempt"""
    success: bool
    job_title: str
    company: str
    platform: str
    message: str
    error: Optional[str] = None


class PlatformApplicationStrategy:
    """Defines application strategies for different platforms"""
    
    STRATEGIES = {
        "naukri": {
            "wait_time": 5,
            "steps": [
                {"action": "click", "selectors": ["button.apply-button", "button[data-ga-track*='apply']", ".btn-apply"]},
                {"action": "fill_form", "fields": "standard"},
                {"action": "upload_resume", "selectors": ["input[type='file']", "#attachCV"]},
                {"action": "click", "selectors": ["button[type='submit']", ".submit-btn"]},
            ]
        },
        "linkedin": {
            "wait_time": 7,
            "steps": [
                {"action": "click", "selectors": ["button.jobs-apply-button", "button[data-control-name*='apply']"]},
                {"action": "wait", "seconds": 2},
                {"action": "fill_form", "fields": "standard"},
                {"action": "click", "selectors": ["button[aria-label='Submit application']", "button[class*='submit']"]},
            ],
            "multi_step": True,
            "next_button_selectors": ["button[aria-label='Continue']", "button[class*='next']"]
        },
        "indeed": {
            "wait_time": 5,
            "steps": [
                {"action": "click", "selectors": ["button.indeedApplyButton", "button[title*='Apply']"]},
                {"action": "fill_form", "fields": "standard"},
                {"action": "upload_resume", "selectors": ["input[type='file']"]},
                {"action": "click", "selectors": ["button[id*='submit']", "button.ia-continueButton"]},
            ]
        },
        "glassdoor": {
            "wait_time": 6,
            "steps": [
                {"action": "click", "selectors": ["button[data-test='apply-button']", ".applyButton"]},
                {"action": "fill_form", "fields": "standard"},
                {"action": "upload_resume", "selectors": ["input[type='file']"]},
                {"action": "click", "selectors": ["button[type='submit']"]},
            ]
        },
        "instahyre": {
            "wait_time": 4,
            "steps": [
                {"action": "click", "selectors": [".apply-btn", "button[class*='apply']"]},
                {"action": "fill_form", "fields": "minimal"},
                {"action": "click", "selectors": ["button[type='submit']"]},
            ]
        },
        "cutshort": {
            "wait_time": 4,
            "steps": [
                {"action": "click", "selectors": [".apply-button", "button[class*='apply']"]},
                {"action": "fill_form", "fields": "standard"},
                {"action": "click", "selectors": ["button.submit-btn"]},
            ]
        },
        "wellfound": {
            "wait_time": 5,
            "steps": [
                {"action": "click", "selectors": ["button[class*='ApplyButton']", ".apply-btn"]},
                {"action": "fill_form", "fields": "minimal"},
                {"action": "click", "selectors": ["button[type='submit']"]},
            ]
        },
        "greenhouse": {
            "wait_time": 6,
            "steps": [
                {"action": "fill_form", "fields": "standard"},
                {"action": "upload_resume", "selectors": ["input#resume_file", "input[type='file']"]},
                {"action": "click", "selectors": ["input[value='Submit Application']", "button#submit_app"]},
            ]
        },
        "lever": {
            "wait_time": 5,
            "steps": [
                {"action": "fill_form", "fields": "standard"},
                {"action": "upload_resume", "selectors": ["input[name='resume']", "input[type='file']"]},
                {"action": "click", "selectors": ["button.template-btn-submit"]},
            ]
        },
        "workday": {
            "wait_time": 8,
            "steps": [
                {"action": "click", "selectors": ["a[data-automation-id='apply']"]},
                {"action": "wait", "seconds": 3},
                {"action": "fill_form", "fields": "standard"},
                {"action": "upload_resume", "selectors": ["input[type='file']"]},
                {"action": "click", "selectors": ["button[data-automation-id='bottom-navigation-next-button']"]},
            ],
            "multi_step": True
        }
    }


class EnhancedJobApplier:
    """Enhanced job application bot with improved reliability"""
    
    def __init__(self, resume_path: str = "temp_resume.pdf"):
        self.resume_path = os.path.abspath(resume_path)
        self.driver = None
        self.wait = None
        self.personal_info = self.load_personal_info()
        self.application_results = []
        self.success_count = 0
        self.failure_count = 0
        
    def initialize_driver(self, headless: bool = False):
        """Initialize Chrome driver with anti-detection"""
        try:
            options = webdriver.ChromeOptions()
            
            # Anti-detection
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
            options.add_argument(f"user-agent={random.choice(user_agents)}")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            # Performance
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-extensions")
            
            if headless:
                options.add_argument("--headless=new")
            
            # Disable images for speed
            prefs = {
                "profile.managed_default_content_settings.images": 2,
                "profile.default_content_setting_values.notifications": 2,
            }
            options.add_experimental_option("prefs", prefs)
            
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
            except:
                self.driver = webdriver.Chrome(options=options)
            
            # Remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.wait = WebDriverWait(self.driver, 15)
            logger.info("✅ Enhanced Chrome driver initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize driver: {e}")
            raise
    
    def load_personal_info(self) -> Dict:
        """Load personal information for applications"""
        try:
            # Try personal_info.json first
            if os.path.exists('personal_info.json'):
                with open('personal_info.json', 'r') as f:
                    return json.load(f)
            # Fallback to example
            elif os.path.exists('personal_info.example.json'):
                with open('personal_info.example.json', 'r') as f:
                    return json.load(f)
            else:
                # Create default
                default_info = {
                    "name": "Manoj Kumar Reddy Koduru",
                    "email": os.getenv('EMAIL_USER', 'your.email@example.com'),
                    "phone": "+91 9381483778",
                    "address": "Kadapa, Andhra Pradesh, India",
                    "linkedin": "https://linkedin.com/in/yourprofile",
                    "website": "https://github.com/yourprofile",
                    "years_experience": "2",
                    "current_company": "Your Company",
                    "notice_period": "Immediate"
                }
                return default_info
        except Exception as e:
            logger.error(f"Error loading personal info: {e}")
            return {}
    
    def human_delay(self, min_sec: float = 1.0, max_sec: float = 3.0):
        """Add human-like delay"""
        time.sleep(random.uniform(min_sec, max_sec))
    
    def detect_platform(self, url: str) -> Optional[str]:
        """Detect platform from URL"""
        url_lower = url.lower()
        platforms = {
            "naukri.com": "naukri",
            "linkedin.com": "linkedin",
            "indeed.com": "indeed",
            "glassdoor": "glassdoor",
            "instahyre.com": "instahyre",
            "cutshort.io": "cutshort",
            "wellfound.com": "wellfound",
            "angellist.com": "wellfound",
            "greenhouse.io": "greenhouse",
            "lever.co": "lever",
            "myworkday.com": "workday",
            "workday.com": "workday"
        }
        
        for key, platform in platforms.items():
            if key in url_lower:
                return platform
        return None
    
    def apply_to_job(self, job_data: Dict) -> ApplicationResult:
        """Apply to a single job with platform-specific strategy"""
        
        job_title = job_data.get('title', 'Unknown')
        company = job_data.get('company', 'Unknown')
        job_link = job_data.get('link', '')
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🎯 Applying to: {job_title} at {company}")
        logger.info(f"🔗 Link: {job_link}")
        
        if not job_link:
            return ApplicationResult(
                success=False,
                job_title=job_title,
                company=company,
                platform="unknown",
                message="No application link provided",
                error="Missing URL"
            )
        
        # Detect platform
        platform = self.detect_platform(job_link)
        if not platform:
            platform = "generic"
        
        logger.info(f"📱 Platform detected: {platform}")
        
        # Initialize driver if needed
        if self.driver is None:
            self.initialize_driver()
        
        try:
            # Navigate to job
            logger.info("🌐 Navigating to job page...")
            self.driver.get(job_link)
            self.human_delay(2, 4)
            
            # Apply platform-specific strategy
            if platform in PlatformApplicationStrategy.STRATEGIES:
                success = self._apply_with_strategy(platform, job_data)
            else:
                success = self._apply_generic(job_data)
            
            if success:
                self.success_count += 1
                result = ApplicationResult(
                    success=True,
                    job_title=job_title,
                    company=company,
                    platform=platform,
                    message="✅ Application submitted successfully!"
                )
                logger.info(f"✅ SUCCESS: Applied to {job_title}")
            else:
                self.failure_count += 1
                result = ApplicationResult(
                    success=False,
                    job_title=job_title,
                    company=company,
                    platform=platform,
                    message="⚠️ Could not complete application",
                    error="Application process incomplete"
                )
                logger.warning(f"⚠️ FAILED: Could not apply to {job_title}")
            
            self.application_results.append(result)
            return result
            
        except Exception as e:
            self.failure_count += 1
            error_msg = str(e)
            logger.error(f"❌ ERROR: {error_msg}")
            
            result = ApplicationResult(
                success=False,
                job_title=job_title,
                company=company,
                platform=platform,
                message="❌ Application failed due to error",
                error=error_msg
            )
            self.application_results.append(result)
            return result
        finally:
            # Clear cookies and cache between applications
            if self.driver:
                try:
                    self.driver.delete_all_cookies()
                except:
                    pass
    
    def _apply_with_strategy(self, platform: str, job_data: Dict) -> bool:
        """Apply using platform-specific strategy"""
        strategy = PlatformApplicationStrategy.STRATEGIES[platform]
        
        logger.info(f"📋 Executing {platform} application strategy")
        
        try:
            for step_num, step in enumerate(strategy["steps"], 1):
                action = step["action"]
                logger.info(f"   Step {step_num}: {action}")
                
                if action == "click":
                    if not self._click_element(step["selectors"]):
                        logger.warning(f"   ⚠️ Click failed at step {step_num}")
                        return False
                    self.human_delay(1, 2)
                
                elif action == "fill_form":
                    field_type = step.get("fields", "standard")
                    self._fill_application_form(field_type)
                    self.human_delay(1, 2)
                
                elif action == "upload_resume":
                    if not self._upload_resume(step["selectors"]):
                        logger.warning(f"   ⚠️ Resume upload failed")
                    self.human_delay(1, 2)
                
                elif action == "wait":
                    seconds = step.get("seconds", 2)
                    time.sleep(seconds)
            
            # Handle multi-step applications
            if strategy.get("multi_step"):
                self._handle_multi_step(strategy.get("next_button_selectors", []))
            
            logger.info("   ✅ All steps completed")
            return True
            
        except Exception as e:
            logger.error(f"   ❌ Strategy execution failed: {e}")
            return False
    
    def _apply_generic(self, job_data: Dict) -> bool:
        """Generic application strategy for unknown platforms"""
        logger.info("📋 Using generic application strategy")
        
        try:
            # Look for apply button
            apply_keywords = ["apply", "submit application", "apply now"]
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            links = self.driver.find_elements(By.TAG_NAME, "a")
            
            for element in buttons + links:
                try:
                    text = element.text.lower()
                    if any(keyword in text for keyword in apply_keywords):
                        logger.info(f"   Found apply button: {element.text}")
                        element.click()
                        self.human_delay(2, 3)
                        break
                except:
                    continue
            
            # Fill any forms found
            self._fill_application_form("standard")
            self.human_delay(1, 2)
            
            # Upload resume if possible
            self._upload_resume(["input[type='file']"])
            self.human_delay(1, 2)
            
            # Try to submit
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button[class*='submit']",
                ".submit-btn",
                ".apply-btn"
            ]
            self._click_element(submit_selectors)
            
            return True
            
        except Exception as e:
            logger.error(f"   ❌ Generic application failed: {e}")
            return False
    
    def _click_element(self, selectors: List[str]) -> bool:
        """Try to click element using multiple selectors"""
        for selector in selectors:
            try:
                element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                # Scroll into view
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                self.human_delay(0.5, 1)
                element.click()
                return True
            except TimeoutException:
                continue
            except Exception as e:
                logger.debug(f"   Click failed for {selector}: {e}")
                continue
        return False
    
    def _fill_application_form(self, field_type: str = "standard"):
        """Fill application form fields"""
        try:
            personal_info = self.personal_info
            
            # Name fields
            name_parts = personal_info.get('name', 'John Doe').split()
            first_name = name_parts[0]
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else 'Doe'
            
            field_mappings = {
                "first_name": ["input[name*='first']", "#firstName", "#first_name", "input[placeholder*='First']"],
                "last_name": ["input[name*='last']", "#lastName", "#last_name", "input[placeholder*='Last']"],
                "full_name": ["input[name*='name']", "#name", "input[placeholder*='Name']"],
                "email": ["input[type='email']", "input[name*='email']", "#email"],
                "phone": ["input[type='tel']", "input[name*='phone']", "#phone"],
                "linkedin": ["input[name*='linkedin']", "#linkedin"],
                "website": ["input[name*='website']", "input[name*='portfolio']", "#website"],
            }
            
            values = {
                "first_name": first_name,
                "last_name": last_name,
                "full_name": personal_info.get('name', 'John Doe'),
                "email": personal_info.get('email', ''),
                "phone": personal_info.get('phone', ''),
                "linkedin": personal_info.get('linkedin', ''),
                "website": personal_info.get('website', ''),
            }
            
            # Additional fields for standard forms
            if field_type == "standard":
                field_mappings.update({
                    "experience": ["input[name*='experience']", "#years_experience"],
                    "current_company": ["input[name*='company']", "#current_company"],
                    "notice": ["input[name*='notice']", "#notice_period"],
                })
                values.update({
                    "experience": personal_info.get('years_experience', '2'),
                    "current_company": personal_info.get('current_company', ''),
                    "notice": personal_info.get('notice_period', 'Immediate'),
                })
            
            # Fill fields
            for field_name, selectors in field_mappings.items():
                value = values.get(field_name, '')
                if value:
                    self._fill_field(selectors, value)
            
            logger.info("   📝 Form fields filled")
            
        except Exception as e:
            logger.warning(f"   ⚠️ Form filling incomplete: {e}")
    
    def _fill_field(self, selectors: List[str], value: str) -> bool:
        """Fill a single form field"""
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        element.clear()
                        element.send_keys(value)
                        return True
            except:
                continue
        return False
    
    def _upload_resume(self, selectors: List[str]) -> bool:
        """Upload resume file"""
        try:
            if not os.path.exists(self.resume_path):
                logger.warning(f"   ⚠️ Resume file not found: {self.resume_path}")
                return False
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.get_attribute('type') == 'file':
                            element.send_keys(self.resume_path)
                            logger.info(f"   📄 Resume uploaded")
                            time.sleep(2)  # Wait for upload
                            return True
                except Exception as e:
                    logger.debug(f"   Upload failed for {selector}: {e}")
                    continue
            return False
        except Exception as e:
            logger.error(f"   ❌ Resume upload error: {e}")
            return False
    
    def _handle_multi_step(self, next_button_selectors: List[str], max_steps: int = 5):
        """Handle multi-step application forms"""
        for step in range(max_steps):
            try:
                # Try to find and click next button
                clicked = self._click_element(next_button_selectors)
                if not clicked:
                    break
                
                self.human_delay(2, 3)
                
                # Fill any new form fields that appear
                self._fill_application_form("standard")
                
            except:
                break
    
    def apply_to_multiple_jobs(
        self,
        jobs: List[Dict],
        max_applications: int = 5,
        delay_between_apps: int = 30
    ) -> Dict:
        """Apply to multiple jobs with rate limiting"""
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🚀 Starting batch application process")
        logger.info(f"📊 Total jobs: {len(jobs)}, Max applications: {max_applications}")
        logger.info(f"{'='*60}\n")
        
        applications_sent = 0
        
        for i, job in enumerate(jobs[:max_applications], 1):
            logger.info(f"\n📝 Processing job {i}/{min(len(jobs), max_applications)}")
            
            result = self.apply_to_job(job)
            
            if result.success:
                applications_sent += 1
            
            # Rate limiting between applications
            if i < min(len(jobs), max_applications):
                logger.info(f"⏳ Waiting {delay_between_apps}s before next application...")
                time.sleep(delay_between_apps)
        
        # Summary
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 APPLICATION SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"✅ Successful: {self.success_count}")
        logger.info(f"❌ Failed: {self.failure_count}")
        logger.info(f"📈 Success Rate: {(self.success_count / max(1, self.success_count + self.failure_count)) * 100:.1f}%")
        logger.info(f"{'='*60}\n")
        
        return {
            "total_attempted": applications_sent + self.failure_count,
            "successful": self.success_count,
            "failed": self.failure_count,
            "results": self.application_results
        }
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            logger.info("🔒 Browser closed")


# Example usage
def main():
    """Example usage"""
    sample_jobs = [
        {
            "title": "Python Developer",
            "company": "Tech Corp",
            "link": "https://www.naukri.com/job-listings-example",
            "location": "Remote"
        }
    ]
    
    applier = EnhancedJobApplier(resume_path="manoj_resume.txt")
    
    try:
        results = applier.apply_to_multiple_jobs(
            jobs=sample_jobs,
            max_applications=3,
            delay_between_apps=30
        )
        print(f"\n✅ Applied to {results['successful']} jobs successfully!")
    finally:
        applier.close()


if __name__ == "__main__":
    main()
