"""
Test script for mail_watcher.py
Demonstrates how to use the MailWatcher class programmatically
"""

import os
from dotenv import load_dotenv
from mail_watcher import MailWatcher

load_dotenv()

def test_mail_watcher_once():
    """Test the mail watcher in one-shot mode"""
    print("="*60)
    print("🧪 Testing Mail Watcher - Single Check")
    print("="*60)
    
    try:
        watcher = MailWatcher(
            poll_interval=60,
            max_applications=2  # Limit to 2 for testing
        )
        
        # Check inbox once
        processed = watcher.check_once()
        
        print("\n" + "="*60)
        print(f"✅ Test Complete! Processed {processed} message(s)")
        print("="*60)
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\nMake sure you have set EMAIL_USER and EMAIL_PASS in your .env file")
        print("For Gmail, use an App Password (not your regular password)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True


def test_with_filters():
    """Test with email filters"""
    print("\n" + "="*60)
    print("🧪 Testing Mail Watcher - With Filters")
    print("="*60)
    
    try:
        watcher = MailWatcher(
            poll_interval=60,
            max_applications=1,
            filter_subject="job"  # Only process emails with "job" in subject
        )
        
        processed = watcher.check_once()
        
        print("\n" + "="*60)
        print(f"✅ Filtered Test Complete! Processed {processed} message(s)")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True


def show_configuration():
    """Display current configuration"""
    print("\n" + "="*60)
    print("⚙️  Current Mail Watcher Configuration")
    print("="*60)
    
    config = {
        'EMAIL_USER': os.getenv('EMAIL_USER', 'NOT SET'),
        'EMAIL_PASS': '***' if os.getenv('EMAIL_PASS') else 'NOT SET',
        'IMAP_SERVER': os.getenv('IMAP_SERVER', 'imap.gmail.com'),
        'IMAP_PORT': os.getenv('IMAP_PORT', '993'),
        'POLL_INTERVAL': os.getenv('POLL_INTERVAL', '60'),
        'MAX_APPLICATIONS': os.getenv('MAX_APPLICATIONS', '3'),
        'RESUME_PATH': os.getenv('RESUME_PATH', 'temp_resume.pdf'),
        'MAIL_FILTER_SENDER': os.getenv('MAIL_FILTER_SENDER', '(none)'),
        'MAIL_FILTER_SUBJECT': os.getenv('MAIL_FILTER_SUBJECT', '(none)')
    }
    
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    print("="*60)
    
    # Check if required values are set
    if os.getenv('EMAIL_USER') and os.getenv('EMAIL_PASS'):
        print("✅ Required configuration found")
        return True
    else:
        print("❌ Missing required configuration (EMAIL_USER and/or EMAIL_PASS)")
        print("\nTo fix:")
        print("1. Copy env.example to .env")
        print("2. Set EMAIL_USER and EMAIL_PASS in .env")
        print("3. For Gmail, use an App Password")
        return False


if __name__ == '__main__':
    print("🚀 ApplyMate Mail Watcher Test Suite\n")
    
    # Show configuration
    config_ok = show_configuration()
    
    if not config_ok:
        print("\n❌ Cannot run tests without proper configuration")
        exit(1)
    
    # Run tests
    print("\n" + "="*60)
    print("Running Tests...")
    print("="*60)
    
    input("\n⏸️  Press Enter to test mail watcher (one-shot mode)...")
    test_result_1 = test_mail_watcher_once()
    
    if test_result_1:
        print("\n✅ Basic test passed!")
        
        user_input = input("\n⏸️  Run filtered test? (y/n): ")
        if user_input.lower() == 'y':
            test_result_2 = test_with_filters()
            
            if test_result_2:
                print("\n✅ All tests passed!")
        
    print("\n" + "="*60)
    print("🎉 Test suite complete!")
    print("="*60)
    print("\nTo run the mail watcher continuously:")
    print("  python mail_watcher.py")
    print("\nTo run it once:")
    print("  set MAIL_WATCHER_MODE=once")
    print("  python mail_watcher.py")
    print("="*60)
