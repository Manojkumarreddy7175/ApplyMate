"""
Enhanced Job Platform Integration Module
Supports multiple platforms with improved reliability, anti-bot detection, and parallel processing
"""

import asyncio
import logging
import time
import random
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JobPlatform(Enum):
    """Supported job platforms"""
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    NAUKRI = "naukri"
    GLASSDOOR = "glassdoor"
    ANGELLIST = "angellist"
    WELLFOUND = "wellfound"
    INSTAHYRE = "instahyre"
    CUTSHORT = "cutshort"
    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    WORKDAY = "workday"


@dataclass
class JobListing:
    """Structured job listing data"""
    title: str
    company: str
    location: str
    link: str
    description: str
    salary: str
    platform: str
    posted_date: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None


class PlatformConfig:
    """Configuration for each job platform"""
    
    PLATFORMS = {
        JobPlatform.LINKEDIN: {
            "base_url": "https://www.linkedin.com/jobs/search",
            "search_params": {
                "keywords": "keywords",
                "location": "location",
                "distance": "distance",
                "f_TP": "1,2"  # Past 24 hours and week
            },
            "selectors": {
                "job_cards": "li.jobs-search-results__list-item",
                "title": "h3.base-search-card__title",
                "company": "h4.base-search-card__subtitle",
                "location": "span.job-search-card__location",
                "link": "a.base-card__full-link",
                "description": "div.show-more-less-html__markup",
                "apply_button": "button[data-control-name='jobdetails_topcard_inapply']"
            },
            "anti_bot": {
                "user_agents": True,
                "delays": (2, 5),
                "stealth": True
            }
        },
        JobPlatform.INDEED: {
            "base_url": "https://in.indeed.com/jobs",
            "search_params": {
                "q": "keywords",
                "l": "location",
                "fromage": "7"  # Last 7 days
            },
            "selectors": {
                "job_cards": "div.job_seen_beacon",
                "title": "h2.jobTitle span",
                "company": "span.companyName",
                "location": "div.companyLocation",
                "link": "h2.jobTitle a",
                "description": "div.jobsearch-JobComponent-description",
                "apply_button": "button[id*='apply'], a[id*='apply']"
            },
            "anti_bot": {
                "user_agents": True,
                "delays": (3, 6),
                "stealth": True
            }
        },
        JobPlatform.NAUKRI: {
            "base_url": "https://www.naukri.com/",
            "search_params": {
                "k": "keywords",
                "l": "location"
            },
            "selectors": {
                "job_cards": "article.jobTuple",
                "title": "a.title",
                "company": "a.subTitle",
                "location": "li.location",
                "link": "a.title",
                "description": "div.job-description",
                "apply_button": "button.apply-button"
            },
            "anti_bot": {
                "user_agents": True,
                "delays": (2, 4),
                "stealth": True
            }
        },
        JobPlatform.GLASSDOOR: {
            "base_url": "https://www.glassdoor.co.in/Job/jobs.htm",
            "search_params": {
                "sc.keyword": "keywords",
                "locT": "C",
                "locId": "location"
            },
            "selectors": {
                "job_cards": "li[data-test='jobListing']",
                "title": "a[data-test='job-link']",
                "company": "div[data-test='employer-name']",
                "location": "div[data-test='emp-location']",
                "link": "a[data-test='job-link']",
                "description": "div[class*='JobDetails_jobDescription']",
                "apply_button": "button[data-test='apply-button']"
            },
            "anti_bot": {
                "user_agents": True,
                "delays": (3, 7),
                "stealth": True
            }
        },
        JobPlatform.INSTAHYRE: {
            "base_url": "https://www.instahyre.com/search-jobs/",
            "search_params": {
                "q": "keywords",
                "l": "location"
            },
            "selectors": {
                "job_cards": "div.opportunity-card",
                "title": "h3.opportunity-title",
                "company": "div.company-name",
                "location": "div.location",
                "link": "a.opportunity-link",
                "description": "div.job-description",
                "apply_button": "button.apply-button"
            },
            "anti_bot": {
                "user_agents": True,
                "delays": (2, 5),
                "stealth": True
            }
        },
        JobPlatform.CUTSHORT: {
            "base_url": "https://cutshort.io/jobs",
            "search_params": {
                "q": "keywords",
                "location": "location"
            },
            "selectors": {
                "job_cards": "div.job-card",
                "title": "h2.job-title",
                "company": "div.company-name",
                "location": "span.location",
                "link": "a.job-link",
                "description": "div.job-desc",
                "apply_button": "button.apply-btn"
            },
            "anti_bot": {
                "user_agents": True,
                "delays": (2, 4),
                "stealth": True
            }
        },
        JobPlatform.WELLFOUND: {
            "base_url": "https://wellfound.com/jobs",
            "search_params": {
                "q": "keywords",
                "l": "location"
            },
            "selectors": {
                "job_cards": "div[class*='JobCard']",
                "title": "a[class*='JobTitle']",
                "company": "div[class*='CompanyName']",
                "location": "div[class*='Location']",
                "link": "a[class*='JobLink']",
                "description": "div.job-description",
                "apply_button": "button[class*='ApplyButton']"
            },
            "anti_bot": {
                "user_agents": True,
                "delays": (3, 6),
                "stealth": True
            }
        }
    }


class EnhancedJobScraper:
    """Enhanced job scraper with anti-bot detection and better reliability"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]
    
    def initialize_driver(self, stealth_mode: bool = True):
        """Initialize Selenium with anti-detection measures"""
        try:
            options = webdriver.ChromeOptions()
            
            # Anti-detection measures
            if stealth_mode:
                options.add_argument(f"user-agent={random.choice(self.user_agents)}")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                options.add_argument("--disable-blink-features=AutomationControlled")
            
            # Performance optimizations
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-gpu")
            prefs = {
                "profile.managed_default_content_settings.images": 2,
                "profile.default_content_setting_values.notifications": 2,
            }
            options.add_experimental_option("prefs", prefs)
            
            # Headless mode (optional)
            # options.add_argument("--headless=new")
            
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
            except Exception as e:
                logger.warning(f"ChromeDriver manager failed: {e}, trying local driver")
                self.driver = webdriver.Chrome(options=options)
            
            # Remove webdriver property
            if stealth_mode:
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.wait = WebDriverWait(self.driver, 15)
            logger.info("Enhanced Chrome driver initialized with anti-detection measures")
            
        except Exception as e:
            logger.error(f"Failed to initialize driver: {e}")
            raise
    
    def human_like_delay(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """Add human-like random delays"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def scroll_page(self, scrolls: int = 3):
        """Scroll page to load dynamic content"""
        for i in range(scrolls):
            self.driver.execute_script(f"window.scrollTo(0, {(i + 1) * 500});")
            self.human_like_delay(0.5, 1.5)
    
    def search_jobs(self, platform: JobPlatform, keywords: str, location: str, max_results: int = 20) -> List[JobListing]:
        """Search jobs on a specific platform"""
        try:
            if self.driver is None:
                self.initialize_driver()
            
            config = PlatformConfig.PLATFORMS.get(platform)
            if not config:
                logger.error(f"Platform {platform} not configured")
                return []
            
            # Build search URL
            base_url = config["base_url"]
            search_params = self._build_search_params(config["search_params"], keywords, location)
            search_url = f"{base_url}?{search_params}"
            
            logger.info(f"Searching {platform.value}: {search_url}")
            
            # Navigate with retry logic
            for attempt in range(3):
                try:
                    self.driver.get(search_url)
                    self.human_like_delay(*config["anti_bot"]["delays"])
                    break
                except Exception as e:
                    if attempt == 2:
                        raise
                    logger.warning(f"Navigation attempt {attempt + 1} failed: {e}")
                    time.sleep(5)
            
            # Scroll to load more jobs
            self.scroll_page()
            
            # Extract job listings
            jobs = self._extract_jobs(platform, config["selectors"], max_results)
            logger.info(f"Found {len(jobs)} jobs on {platform.value}")
            
            return jobs
            
        except Exception as e:
            logger.error(f"Error searching {platform.value}: {e}")
            return []
    
    def _build_search_params(self, param_mapping: Dict, keywords: str, location: str) -> str:
        """Build search query parameters"""
        params = []
        for key, value in param_mapping.items():
            if value == "keywords":
                params.append(f"{key}={keywords.replace(' ', '+')}")
            elif value == "location":
                params.append(f"{key}={location.replace(' ', '+')}")
            else:
                params.append(f"{key}={value}")
        return "&".join(params)
    
    def _extract_jobs(self, platform: JobPlatform, selectors: Dict, max_results: int) -> List[JobListing]:
        """Extract job listings from page"""
        jobs = []
        
        try:
            # Wait for job cards to load
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selectors["job_cards"])))
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, selectors["job_cards"])[:max_results]
            
            for card in job_cards:
                try:
                    # Extract job data with multiple fallback selectors
                    title = self._safe_extract(card, selectors["title"])
                    company = self._safe_extract(card, selectors["company"])
                    location = self._safe_extract(card, selectors["location"])
                    link = self._safe_extract_attribute(card, selectors["link"], "href")
                    
                    # Get full URL
                    if link and not link.startswith("http"):
                        link = self.driver.current_url.split("?")[0].rsplit("/", 1)[0] + link
                    
                    if title and company and link:
                        job = JobListing(
                            title=title,
                            company=company,
                            location=location or "Remote",
                            link=link,
                            description="",  # Will be fetched when needed
                            salary="Not specified",
                            platform=platform.value
                        )
                        jobs.append(job)
                
                except Exception as e:
                    logger.debug(f"Error extracting job card: {e}")
                    continue
            
        except TimeoutException:
            logger.warning(f"Timeout waiting for jobs on {platform.value}")
        except Exception as e:
            logger.error(f"Error extracting jobs: {e}")
        
        return jobs
    
    def _safe_extract(self, element, selector: str) -> str:
        """Safely extract text from element"""
        try:
            # Try multiple selector strategies
            for sel in selector.split(","):
                sel = sel.strip()
                try:
                    found = element.find_element(By.CSS_SELECTOR, sel)
                    text = found.text.strip()
                    if text:
                        return text
                except:
                    continue
            return ""
        except:
            return ""
    
    def _safe_extract_attribute(self, element, selector: str, attribute: str) -> str:
        """Safely extract attribute from element"""
        try:
            for sel in selector.split(","):
                sel = sel.strip()
                try:
                    found = element.find_element(By.CSS_SELECTOR, sel)
                    attr = found.get_attribute(attribute)
                    if attr:
                        return attr
                except:
                    continue
            return ""
        except:
            return ""
    
    def get_job_description(self, job: JobListing) -> str:
        """Fetch full job description"""
        try:
            self.driver.get(job.link)
            self.human_like_delay(2, 4)
            
            # Try multiple common description selectors
            description_selectors = [
                "div.job-description",
                "div.description",
                "div.show-more-less-html__markup",
                "div[class*='description']",
                "div[id*='description']",
                "section.description"
            ]
            
            for selector in description_selectors:
                try:
                    desc_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    return desc_element.text.strip()
                except:
                    continue
            
            # Fallback: get body text
            body = self.driver.find_element(By.TAG_NAME, "body")
            return body.text[:1000]  # First 1000 chars
            
        except Exception as e:
            logger.error(f"Error fetching job description: {e}")
            return ""
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")


class ParallelJobSearcher:
    """Search multiple platforms in parallel"""
    
    def __init__(self):
        self.scrapers = {}
    
    async def search_all_platforms(
        self,
        platforms: List[JobPlatform],
        keywords: str,
        location: str,
        max_results_per_platform: int = 20
    ) -> List[JobListing]:
        """Search multiple platforms in parallel"""
        
        logger.info(f"Starting parallel search across {len(platforms)} platforms")
        
        # Create tasks for each platform
        tasks = []
        for platform in platforms:
            task = self._search_platform_async(platform, keywords, location, max_results_per_platform)
            tasks.append(task)
        
        # Run all searches concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        all_jobs = []
        for result in results:
            if isinstance(result, list):
                all_jobs.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Platform search failed: {result}")
        
        logger.info(f"Total jobs found across all platforms: {len(all_jobs)}")
        return all_jobs
    
    async def _search_platform_async(
        self,
        platform: JobPlatform,
        keywords: str,
        location: str,
        max_results: int
    ) -> List[JobListing]:
        """Async wrapper for platform search"""
        loop = asyncio.get_event_loop()
        scraper = EnhancedJobScraper()
        
        try:
            # Run search in thread pool to avoid blocking
            jobs = await loop.run_in_executor(
                None,
                scraper.search_jobs,
                platform,
                keywords,
                location,
                max_results
            )
            return jobs
        except Exception as e:
            logger.error(f"Error in async search for {platform.value}: {e}")
            return []
        finally:
            scraper.close()


class JobPlatformManager:
    """Main manager for job platform operations"""
    
    def __init__(self):
        self.parallel_searcher = ParallelJobSearcher()
        self.scraper = None
    
    async def search_jobs(
        self,
        keywords: str,
        location: str = "India",
        platforms: Optional[List[JobPlatform]] = None,
        max_results_per_platform: int = 20,
        parallel: bool = True
    ) -> List[JobListing]:
        """Search jobs across multiple platforms"""
        
        if platforms is None:
            # Default to popular Indian platforms
            platforms = [
                JobPlatform.NAUKRI,
                JobPlatform.LINKEDIN,
                JobPlatform.INDEED,
                JobPlatform.INSTAHYRE,
                JobPlatform.GLASSDOOR,
                JobPlatform.CUTSHORT,
                JobPlatform.WELLFOUND
            ]
        
        if parallel:
            jobs = await self.parallel_searcher.search_all_platforms(
                platforms, keywords, location, max_results_per_platform
            )
        else:
            # Sequential search
            jobs = []
            self.scraper = EnhancedJobScraper()
            try:
                for platform in platforms:
                    platform_jobs = self.scraper.search_jobs(
                        platform, keywords, location, max_results_per_platform
                    )
                    jobs.extend(platform_jobs)
            finally:
                if self.scraper:
                    self.scraper.close()
        
        return jobs
    
    def filter_jobs(
        self,
        jobs: List[JobListing],
        skills: List[str],
        min_salary: Optional[int] = None,
        experience_level: Optional[str] = None
    ) -> List[JobListing]:
        """Filter jobs based on criteria"""
        
        filtered = []
        for job in jobs:
            score = 0
            
            # Check skills match
            title_desc = f"{job.title} {job.description}".lower()
            for skill in skills:
                if skill.lower() in title_desc:
                    score += 1
            
            # Basic filtering
            if score > 0:
                filtered.append(job)
        
        logger.info(f"Filtered {len(filtered)} jobs out of {len(jobs)}")
        return filtered
    
    def remove_duplicates(self, jobs: List[JobListing]) -> List[JobListing]:
        """Remove duplicate job listings"""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            identifier = f"{job.title}_{job.company}".lower()
            if identifier not in seen:
                seen.add(identifier)
                unique_jobs.append(job)
        
        logger.info(f"Removed {len(jobs) - len(unique_jobs)} duplicates")
        return unique_jobs


# Example usage
async def main():
    """Example usage of enhanced job platform system"""
    
    manager = JobPlatformManager()
    
    # Search for jobs
    jobs = await manager.search_jobs(
        keywords="Python Developer AI Machine Learning",
        location="India",
        max_results_per_platform=10,
        parallel=True
    )
    
    # Remove duplicates
    unique_jobs = manager.remove_duplicates(jobs)
    
    # Filter by skills
    filtered_jobs = manager.filter_jobs(
        unique_jobs,
        skills=["Python", "AI", "Machine Learning", "Django", "Flask"],
        min_salary=800000
    )
    
    # Display results
    for i, job in enumerate(filtered_jobs[:10], 1):
        print(f"\n{i}. {job.title}")
        print(f"   Company: {job.company}")
        print(f"   Location: {job.location}")
        print(f"   Platform: {job.platform}")
        print(f"   Link: {job.link}")


if __name__ == "__main__":
    asyncio.run(main())
