#!/usr/bin/env python3
"""
Vacancy scheduler
Automated scheduling for vacancy filtering
"""

import asyncio
import schedule
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict

from ks_reporter.common.utils import setup_logging, validate_environment
from ks_reporter.vacancy.filter import VacancyFilter

logger = logging.getLogger(__name__)


class VacancyScheduler:
    """Scheduler for automated vacancy checking"""

    def __init__(self, session_name: str = 'session-3', target_user: int = 258610595):
        self.session_name = session_name
        self.target_user = target_user
        self.last_run = None

        # Load configuration
        try:
            import json
            with open('vacancy_config.json', 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            logger.warning("⚠️ No vacancy_config.json found, using defaults")
            self.config = {
                "filtering_config": {
                    "check_interval_hours": 6,
                    "max_results_to_send": 10
                }
            }

    async def run_vacancy_check(self):
        """Run a single vacancy check cycle"""
        logger.info("🔄 Starting scheduled vacancy check...")

        try:
            # Initialize filter
            vacancy_filter = VacancyFilter(self.session_name)

            # Get channels (you might want to cache this)
            channels = await vacancy_filter.discover_channels()
            vacancy_filter.job_channels = vacancy_filter.select_job_channels(channels)

            if not vacancy_filter.job_channels:
                logger.warning("⚠️ No job channels configured")
                return

            # Check how long since last run
            hours_back = self.config['filtering_config'].get('check_interval_hours', 6)
            if self.last_run:
                time_diff = datetime.now() - self.last_run
                hours_back = min(hours_back, int(time_diff.total_seconds() / 3600) + 1)

            # Fetch and filter messages
            messages = await vacancy_filter.fetch_new_messages(hours_back)

            if not messages:
                logger.info("📭 No new messages to process")
                self.last_run = datetime.now()
                return

            # Filter vacancies
            vacancy_results = await vacancy_filter.filter_vacancies(messages)

            if vacancy_results:
                top_vacancies = vacancy_filter.rank_and_filter_vacancies(vacancy_results)

                if top_vacancies:
                    # Check if we should send results
                    if self._should_send_now():
                        await vacancy_filter.send_results(top_vacancies, self.target_user)
                        logger.info(f"✅ Sent {len(top_vacancies)} vacancy matches")
                    else:
                        logger.info("🔇 Quiet hours - results saved but not sent")
                        # Save for later
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        vacancy_filter.data_manager.save_json(
                            top_vacancies,
                            f"pending_vacancies_{timestamp}.json"
                        )
                else:
                    logger.info("📭 No high-quality matches found")

            self.last_run = datetime.now()
            logger.info("✅ Vacancy check completed")

        except Exception as e:
            logger.error(f"❌ Scheduled vacancy check failed: {e}")

    def _should_send_now(self) -> bool:
        """Check if we should send notifications now (respect quiet hours)"""
        quiet_settings = self.config.get('notification_settings', {}).get('quiet_hours')

        if not quiet_settings:
            return True

        try:
            now = datetime.now().time()
            start_time = datetime.strptime(quiet_settings['start'], '%H:%M').time()
            end_time = datetime.strptime(quiet_settings['end'], '%H:%M').time()

            # Handle quiet hours that span midnight
            if start_time > end_time:
                return not (now >= start_time or now <= end_time)
            else:
                return not (start_time <= now <= end_time)

        except (KeyError, ValueError):
            return True

    def setup_schedule(self):
        """Setup the checking schedule"""
        check_interval = self.config['filtering_config'].get('check_interval_hours', 6)

        # Schedule regular checks
        schedule.every(check_interval).hours.do(
            lambda: asyncio.create_task(self.run_vacancy_check())
        )

        # Schedule daily summary (optional)
        if self.config.get('notification_settings', {}).get('send_daily_summary', False):
            schedule.every().day.at("09:00").do(
                lambda: asyncio.create_task(self.send_daily_summary())
            )

        logger.info(f"📅 Scheduled vacancy checks every {check_interval} hours")

    async def send_daily_summary(self):
        """Send daily summary of vacancy activity"""
        logger.info("📊 Generating daily summary...")

        # Look for vacancy results from the last 24 hours
        data_dir = Path("data")
        yesterday = datetime.now() - timedelta(days=1)

        summary_data = {
            'total_messages_processed': 0,
            'vacancies_found': 0,
            'top_matches': 0,
            'channels_checked': 0
        }

        # This is a simplified summary - you might want to enhance it
        summary_message = f"""📊 **Daily Vacancy Summary**
        
🔍 Channels monitored: {summary_data['channels_checked']}
📨 Messages processed: {summary_data['total_messages_processed']}
🎯 Vacancies found: {summary_data['vacancies_found']}
🏆 Top matches: {summary_data['top_matches']}

📅 {datetime.now().strftime('%Y-%m-%d')}"""

        # Send summary (implementation depends on your needs)
        logger.info("📊 Daily summary generated")

    def run_forever(self):
        """Run the scheduler continuously"""
        logger.info("🚀 Starting vacancy scheduler...")

        self.setup_schedule()

        # Run initial check
        asyncio.run(self.run_vacancy_check())

        # Keep running scheduled jobs
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
