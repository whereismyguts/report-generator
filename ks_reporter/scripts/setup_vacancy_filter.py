#!/usr/bin/env python3
"""
Vacancy filter setup script
Helps with initial configuration and testing of vacancy filter
"""

import asyncio
import json
import os
import logging
import argparse
from pathlib import Path

from ks_reporter.common.utils import setup_logging, validate_environment
from ks_reporter.vacancy.filter import VacancyFilter

logger = logging.getLogger(__name__)


async def setup_channels():
    """Interactive setup for job channels"""
    print("🔍 **Channel Discovery & Setup**\n")
    
    # Initialize filter
    vacancy_filter = VacancyFilter()
    
    # Discover channels
    channels = await vacancy_filter.discover_channels()
    
    if not channels:
        print("❌ No channels found. Make sure you're subscribed to some Telegram channels.")
        return
    
    print(f"📱 Found {len(channels)} channels. Select job-related channels:\n")
    
    # Display channels with numbers
    for i, channel in enumerate(channels, 1):
        unread = f" ({channel['unread_count']} unread)" if channel['unread_count'] > 0 else ""
        username = f" @{channel['username']}" if channel['username'] else ""
        print(f"{i:2d}. {channel['title']}{username}{unread}")
        print(f"     ID: {channel['id']}")
    
    print("\n💡 Enter the numbers of job channels (space-separated), or 'auto' for auto-detection:")
    selection = input("> ").strip()
    
    selected_channels = []
    
    if selection.lower() == 'auto':
        selected_channels = vacancy_filter.select_job_channels(channels)
        print(f"🤖 Auto-selected {len(selected_channels)} channels:")
    else:
        try:
            indices = [int(i) - 1 for i in selection.split()]
            selected_channels = [channels[i] for i in indices if 0 <= i < len(channels)]
            print(f"✅ Selected {len(selected_channels)} channels:")
        except (ValueError, IndexError):
            print("❌ Invalid selection. Using auto-detection instead.")
            selected_channels = vacancy_filter.select_job_channels(channels)
    
    # Display selected channels
    for channel in selected_channels:
        print(f"  - {channel['title']} (ID: {channel['id']})")
    
    # Save to config
    config_path = Path('vacancy_config.json')
    
    try:
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {
                "job_channels": {},
                "filtering_config": {
                    "check_interval_hours": 6,
                    "max_messages_per_channel": 200,
                    "min_score_threshold": 0.4,
                    "max_results_to_send": 10,
                    "auto_send_results": True
                },
                "notification_settings": {
                    "send_daily_summary": True,
                    "send_immediate_alerts": True,
                    "quiet_hours": {
                        "start": "22:00",
                        "end": "08:00"
                    }
                }
            }
        
        # Update job channels
        config["job_channels"] = {}
        for channel in selected_channels:
            key = f"channel_{channel['id']}"
            config["job_channels"][key] = {
                "id": channel['id'],
                "title": channel['title'],
                "username": channel['username'],
                "enabled": True
            }
        
        # Save config
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
        print(f"✅ Configuration saved to {config_path}")
            
    except Exception as e:
        print(f"❌ Failed to save configuration: {e}")


async def test_vacancy_filtering():
    """Test the vacancy filtering system"""
    print("\n🧪 **Testing Vacancy Filtering**\n")
    
    # Initialize filter
    vacancy_filter = VacancyFilter()
    
    # Load channels from config
    config_path = Path('vacancy_config.json')
    if not config_path.exists():
        print("❌ No configuration found. Run setup first.")
        return
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Get channel data
    channels = await vacancy_filter.discover_channels()
    
    # Map config to channels
    job_channels = []
    for channel_config in config.get('job_channels', {}).values():
        channel_id = channel_config.get('id')
        if channel_id and channel_config.get('enabled', True):
            matching_channel = next((ch for ch in channels if ch['id'] == channel_id), None)
            if matching_channel:
                job_channels.append(matching_channel)
    
    vacancy_filter.job_channels = job_channels
    
    if not job_channels:
        print("❌ No enabled job channels found in configuration.")
        return
    
    print(f"📊 Testing with {len(job_channels)} channels...")
    
    # Fetch recent messages
    messages = await vacancy_filter.fetch_new_messages(hours_back=48)
    
    if not messages:
        print("📭 No recent messages found to test with.")
        return
    
    print(f"📨 Found {len(messages)} recent messages")
    
    # Test AI filtering (dry run)
    print("🤖 Testing AI filtering...")
    vacancy_results = await vacancy_filter.filter_vacancies(messages)
    
    if vacancy_results:
        top_vacancies = vacancy_filter.rank_and_filter_vacancies(vacancy_results)
        
        if top_vacancies:
            print(f"✅ Found {len(top_vacancies)} matching vacancies!")
            
            # Display results
            formatted_message = vacancy_filter.format_vacancy_message(top_vacancies, messages)
            print("\n" + "="*50)
            print(formatted_message)
            print("="*50)
        else:
            print("📭 No high-quality matches found in test data.")
    else:
        print("❌ AI filtering test failed.")


def check_environment():
    """Check environment setup"""
    print("🔍 **Checking Environment**\n")
    
    try:
        validate_environment()
        print("✅ Environment validation passed")
    except ValueError as e:
        print(f"❌ {str(e)}")
        print("\n💡 Create a .env file with the following variables:")
        print("""
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=your_phone_number
OPENROUTER_API_KEY=your_openrouter_key
""")


def check_files():
    """Check required files"""
    print("\n🔍 **Checking Required Files**\n")
    
    # Check resume.json
    resume_path = Path('resume.json')
    if resume_path.exists():
        try:
            with open(resume_path, 'r', encoding='utf-8') as f:
                resume = json.load(f)
            print("✅ resume.json found and valid")
             
        except json.JSONDecodeError:
            print("❌ resume.json exists but contains invalid JSON")
    else:
        print("❌ resume.json not found")
        print("💡 Create a resume.json file with your skills and preferences")
    
    # Check prompt template
    prompt_path = Path('vacancy-filter-prompt.md')
    if prompt_path.exists():
        print("✅ vacancy-filter-prompt.md found")
    else:
        print("❌ vacancy-filter-prompt.md not found")
        print("💡 Create a prompt template for vacancy filtering")


async def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description="Setup vacancy filtering system")
    parser.add_argument('--check-only', action='store_true', help='Only check environment without setup')
    args = parser.parse_args()
    
    setup_logging("setup_vacancy_filter.log")
    
    print("🔧 **Vacancy Filter Setup**\n")
    
    try:
        # Check environment and files
        check_environment()
        check_files()
        
        if args.check_only:
            return
            
        # Setup channels
        choice = input("\nSetup job channels? (y/n): ").strip().lower()
        if choice == 'y':
            await setup_channels()
            
        # Test filtering
        choice = input("\nTest vacancy filtering? (y/n): ").strip().lower()
        if choice == 'y':
            await test_vacancy_filtering()
            
        print("\n✅ Setup completed")
        print("\n💡 Run the vacancy filter with:")
        print("    python -m ks_reporter.scripts.run_vacancy_filter")
        print("\n💡 Or schedule automated checks with:")
        print("    python -m ks_reporter.scripts.run_vacancy_scheduler")
            
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        logger.exception("Setup failed")


if __name__ == "__main__":
    asyncio.run(main())
