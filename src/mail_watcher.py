"""
Mail Watcher Module
Monitors IMAP inbox for new job notification emails and automatically applies via browser automation.

This module:
1. Polls an IMAP inbox for unseen messages
2. Extracts job application links from email content
3. Triggers EnhancedJobApplier to automatically apply to jobs
4. Marks processed emails as seen

Configuration via environment variables:
- EMAIL_USER: IMAP username (required)
- EMAIL_PASS: IMAP password/app password (required)
- IMAP_SERVER: IMAP server address (default: imap.gmail.com)
- IMAP_PORT: IMAP port (default: 993)
- POLL_INTERVAL: Seconds between inbox checks (default: 60)
- MAX_APPLICATIONS: Max jobs to apply per email (default: 3)
- RESUME_PATH: Path to resume file (default: temp_resume.pdf)
- MAIL_FILTER_SENDER: Only process emails from specific sender (optional)
- MAIL_FILTER_SUBJECT: Only process emails with subject containing text (optional)
"""

import imaplib
import email
from email.header import decode_header
import os
import re
import time
import logging
from typing import List, Dict, Optional
from dotenv import load_dotenv

from enhanced_job_applier import EnhancedJobApplier

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MailWatcher:
    """Monitors IMAP inbox and triggers job applications"""
    
    def __init__(
        self,
        imap_server: str = None,
        imap_port: int = None,
        email_user: str = None,
        email_pass: str = None,
        resume_path: str = None,
        poll_interval: int = 60,
        max_applications: int = 3,
        filter_sender: str = None,
        filter_subject: str = None
    ):
        self.imap_server = imap_server or os.getenv('IMAP_SERVER', 'imap.gmail.com')
        self.imap_port = imap_port or int(os.getenv('IMAP_PORT', '993'))
        self.email_user = email_user or os.getenv('EMAIL_USER')
        self.email_pass = email_pass or os.getenv('EMAIL_PASS')
        self.resume_path = resume_path or os.getenv('RESUME_PATH', 'temp_resume.pdf')
        self.poll_interval = poll_interval
        self.max_applications = max_applications
        self.filter_sender = filter_sender or os.getenv('MAIL_FILTER_SENDER')
        self.filter_subject = filter_subject or os.getenv('MAIL_FILTER_SUBJECT')
        
        if not self.email_user or not self.email_pass:
            raise ValueError("EMAIL_USER and EMAIL_PASS must be configured")
        
        if not os.path.exists(self.resume_path):
            logger.warning(f"Resume file not found: {self.resume_path}")
    
    def decode_email_header(self, header_value: str) -> str:
        """Decode email header that may contain encoded content"""
        if not header_value:
            return ""
        
        decoded_parts = decode_header(header_value)
        result = []
        
        for content, encoding in decoded_parts:
            if isinstance(content, bytes):
                try:
                    result.append(content.decode(encoding or 'utf-8', errors='ignore'))
                except:
                    result.append(content.decode('utf-8', errors='ignore'))
            else:
                result.append(str(content))
        
        return ''.join(result)
    
    def extract_links_from_message(self, msg: email.message.Message) -> List[str]:
        """Extract HTTP/HTTPS URLs from email message body"""
        links = []
        
        # Extract text content from email
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                
                if content_type in ('text/plain', 'text/html'):
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            text = payload.decode(errors='ignore')
                            links.extend(self._find_urls_in_text(text))
                    except Exception as e:
                        logger.debug(f"Error extracting from part: {e}")
        else:
            try:
                payload = msg.get_payload(decode=True)
                if payload:
                    text = payload.decode(errors='ignore')
                    links.extend(self._find_urls_in_text(text))
            except Exception as e:
                logger.debug(f"Error extracting payload: {e}")
        
        # Deduplicate while preserving order
        seen = set()
        unique_links = []
        for link in links:
            # Clean up common email artifacts
            link = link.rstrip('.,;)')
            if link not in seen and self._is_valid_job_url(link):
                seen.add(link)
                unique_links.append(link)
        
        return unique_links
    
    def _find_urls_in_text(self, text: str) -> List[str]:
        """Extract URLs from text using regex"""
        # Match HTTP/HTTPS URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+(?:[^\s<>"{}|\\^`\[\].,;:!?\'\)]|(?:[.,;:!?\'\)](?=[^\s])))*'
        urls = re.findall(url_pattern, text)
        return urls
    
    def _is_valid_job_url(self, url: str) -> bool:
        """Check if URL is likely a job application link"""
        # Filter out common non-job URLs
        exclude_patterns = [
            'unsubscribe', 'privacy', 'terms', 'contact',
            'facebook.com', 'twitter.com', 'instagram.com',
            'linkedin.com/feed', 'linkedin.com/in/',
            'youtube.com', 'support.', 'help.'
        ]
        
        url_lower = url.lower()
        
        # Exclude non-job URLs
        if any(pattern in url_lower for pattern in exclude_patterns):
            return False
        
        # Prefer job-related URLs
        job_indicators = [
            'job', 'career', 'apply', 'position', 'opportunity',
            'naukri.com', 'indeed.com', 'linkedin.com/jobs',
            'glassdoor', 'instahyre', 'cutshort', 'wellfound',
            'greenhouse.io', 'lever.co', 'workday.com'
        ]
        
        return any(indicator in url_lower for indicator in job_indicators)
    
    def should_process_email(self, sender: str, subject: str) -> bool:
        """Check if email matches filter criteria"""
        if self.filter_sender and self.filter_sender.lower() not in sender.lower():
            logger.debug(f"Email from {sender} doesn't match sender filter")
            return False
        
        if self.filter_subject and self.filter_subject.lower() not in subject.lower():
            logger.debug(f"Email subject '{subject}' doesn't match subject filter")
            return False
        
        return True
    
    def build_job_data_from_links(
        self,
        links: List[str],
        email_subject: str,
        email_sender: str
    ) -> List[Dict]:
        """Convert extracted links into job data dictionaries"""
        jobs = []
        
        for link in links:
            job = {
                'title': f'Job from email: {email_subject[:50]}',
                'company': self._extract_company_from_sender(email_sender),
                'link': link,
                'location': 'Remote/Not Specified',
                'description': f'Auto-extracted from email notification from {email_sender}',
                'salary': 'Not specified'
            }
            jobs.append(job)
        
        return jobs
    
    def _extract_company_from_sender(self, sender: str) -> str:
        """Try to extract company name from email sender"""
        # Extract name before @ in email addresses
        match = re.search(r'([^@<]+)@', sender)
        if match:
            return match.group(1).replace('.', ' ').title()
        
        # Extract name from "Name <email>" format
        match = re.search(r'^([^<]+)<', sender)
        if match:
            return match.group(1).strip()
        
        return 'Unknown Company'
    
    def process_unseen_messages(self) -> int:
        """
        Connect to IMAP, process unseen messages, and trigger applications.
        Returns number of messages processed.
        """
        processed_count = 0
        
        try:
            # Connect to IMAP server
            logger.info(f"Connecting to {self.imap_server}:{self.imap_port}")
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_user, self.email_pass)
            logger.info("✅ IMAP login successful")
            
        except Exception as e:
            logger.error(f"❌ IMAP connection failed: {e}")
            return 0
        
        try:
            # Select inbox
            mail.select('INBOX')
            
            # Search for unseen messages
            status, message_ids = mail.search(None, 'UNSEEN')
            
            if status != 'OK':
                logger.warning("Failed to search for unseen messages")
                return 0
            
            msg_id_list = message_ids[0].split()
            
            if not msg_id_list:
                logger.debug("No unseen messages found")
                return 0
            
            logger.info(f"📧 Found {len(msg_id_list)} unseen message(s)")
            
            # Process each message
            for msg_id in msg_id_list:
                try:
                    self._process_single_message(mail, msg_id)
                    processed_count += 1
                except Exception as e:
                    logger.error(f"Error processing message {msg_id}: {e}")
                    # Mark as seen anyway to avoid reprocessing
                    try:
                        mail.store(msg_id, '+FLAGS', '\\Seen')
                    except:
                        pass
            
            return processed_count
            
        finally:
            try:
                mail.close()
            except:
                pass
            mail.logout()
    
    def _process_single_message(self, mail: imaplib.IMAP4_SSL, msg_id: bytes):
        """Process a single email message"""
        # Fetch message
        status, msg_data = mail.fetch(msg_id, '(RFC822)')
        
        if status != 'OK' or not msg_data or not msg_data[0]:
            logger.warning(f"Failed to fetch message {msg_id}")
            return
        
        # Parse email
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        
        # Extract headers
        subject = self.decode_email_header(msg.get('Subject', '(no subject)'))
        sender = self.decode_email_header(msg.get('From', ''))
        date = msg.get('Date', '')
        
        logger.info(f"\n{'='*60}")
        logger.info(f"📨 Processing Email")
        logger.info(f"From: {sender}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Date: {date}")
        logger.info(f"{'='*60}")
        
        # Check filters
        if not self.should_process_email(sender, subject):
            logger.info("⏭️  Email doesn't match filters, marking as seen")
            mail.store(msg_id, '+FLAGS', '\\Seen')
            return
        
        # Extract links
        links = self.extract_links_from_message(msg)
        
        if not links:
            logger.info("ℹ️  No job links found in email, marking as seen")
            mail.store(msg_id, '+FLAGS', '\\Seen')
            return
        
        logger.info(f"🔗 Found {len(links)} potential job link(s):")
        for i, link in enumerate(links[:5], 1):  # Show first 5
            logger.info(f"   {i}. {link[:80]}...")
        
        # Build job data
        jobs = self.build_job_data_from_links(links, subject, sender)
        
        # Apply to jobs
        logger.info(f"\n🚀 Triggering applications (max {self.max_applications})...")
        
        applier = EnhancedJobApplier(resume_path=self.resume_path)
        
        try:
            results = applier.apply_to_multiple_jobs(
                jobs=jobs,
                max_applications=self.max_applications,
                delay_between_apps=10  # 10 seconds between applications
            )
            
            logger.info(f"\n📊 Application Results:")
            logger.info(f"   ✅ Successful: {results['successful']}")
            logger.info(f"   ❌ Failed: {results['failed']}")
            logger.info(f"   📈 Total Attempted: {results['total_attempted']}")
            
        except Exception as e:
            logger.error(f"❌ Application process failed: {e}")
        finally:
            applier.close()
        
        # Mark email as seen after processing
        mail.store(msg_id, '+FLAGS', '\\Seen')
        logger.info("✔️  Email marked as processed\n")
    
    def start_watching(self):
        """Start the mail watcher loop (runs indefinitely)"""
        logger.info("\n" + "="*60)
        logger.info("📬 Mail Watcher Started")
        logger.info("="*60)
        logger.info(f"Server: {self.imap_server}:{self.imap_port}")
        logger.info(f"User: {self.email_user}")
        logger.info(f"Poll Interval: {self.poll_interval}s")
        logger.info(f"Max Applications/Email: {self.max_applications}")
        logger.info(f"Resume: {self.resume_path}")
        
        if self.filter_sender:
            logger.info(f"Filter Sender: {self.filter_sender}")
        if self.filter_subject:
            logger.info(f"Filter Subject: {self.filter_subject}")
        
        logger.info("="*60 + "\n")
        logger.info("👀 Watching for new emails... (Ctrl+C to stop)")
        
        try:
            while True:
                try:
                    processed = self.process_unseen_messages()
                    
                    if processed > 0:
                        logger.info(f"✅ Processed {processed} message(s)")
                    
                except Exception as e:
                    logger.exception(f"❌ Error in processing loop: {e}")
                
                # Wait before next check
                time.sleep(self.poll_interval)
                
        except KeyboardInterrupt:
            logger.info("\n\n🛑 Mail watcher stopped by user")
    
    def check_once(self) -> int:
        """Check inbox once and process messages (for testing/manual runs)"""
        logger.info("🔍 Checking inbox once...")
        processed = self.process_unseen_messages()
        logger.info(f"✅ Check complete. Processed {processed} message(s)")
        return processed


def main():
    """Main entry point"""
    # Load configuration from environment
    config = {
        'poll_interval': int(os.getenv('POLL_INTERVAL', '60')),
        'max_applications': int(os.getenv('MAX_APPLICATIONS', '3'))
    }
    
    try:
        watcher = MailWatcher(**config)
        
        # Check if running in one-shot mode
        if os.getenv('MAIL_WATCHER_MODE') == 'once':
            watcher.check_once()
        else:
            watcher.start_watching()
            
    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        logger.error("Please ensure EMAIL_USER and EMAIL_PASS are set in .env file")
        return 1
    except Exception as e:
        logger.exception(f"❌ Fatal error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
