#!/usr/bin/env python3
"""
Vacancy filter script
Checks for new job vacancies that match the user's resume
"""

import asyncio
import argparse
import logging

from ks_reporter.common.utils import setup_logging, validate_environment
from ks_reporter.vacancy.filter import VacancyFilter

logger = logging.getLogger(__name__)


async def main():
    """Run the vacancy filtering process"""
    parser = argparse.ArgumentParser(description="Filter job vacancies from Telegram channels")
    parser.add_argument('--discover', action='store_true', help='Discover and list available channels')
    parser.add_argument('--channels', nargs='+', type=int, help='Specific channel IDs to monitor')
    parser.add_argument('--hours', type=int, default=24, help='Hours back to check for new messages')
    parser.add_argument('--session', default='session-3', help='Telegram session name')
    parser.add_argument('--target-user', type=int, default=258610595, help='Target user ID for results')
    parser.add_argument('--dry-run', action='store_true', help='Process vacancies but don\'t send results')

    args = parser.parse_args()

    # Setup logging
    setup_logging("vacancy_filter.log")

    # Validate environment
    validate_environment()

    try:
        # Initialize filter
        vacancy_filter = VacancyFilter(args.session)

        if args.discover:
            # Discovery mode - list all channels
            channels = await vacancy_filter.discover_channels()

            print("\n🔍 **Available Channels:**")
            for i, channel in enumerate(channels, 1):
                unread = f" ({channel['unread_count']} unread)" if channel['unread_count'] > 0 else ""
                username = f" @{channel['username']}" if channel['username'] else ""
                print(f"{i:2d}. {channel['title']}{username}{unread}")
                print(f"     ID: {channel['id']}")

            print(f"\n💡 Use --channels with specific IDs to monitor job channels")
            return

        # Regular filtering mode
        logger.info("🚀 Starting vacancy filtering process...")

        # Get available channels
        channels = await vacancy_filter.discover_channels()

        # Select job channels
        vacancy_filter.job_channels = vacancy_filter.select_job_channels(channels, args.channels)

        if not vacancy_filter.job_channels:
            logger.error("❌ No job channels selected. Use --discover to see available channels.")
            return

        # Fetch new messages
        messages = await vacancy_filter.fetch_new_messages(args.hours)

        if not messages:
            logger.info("📭 No new messages found")
            return

        # Filter vacancies with AI
        vacancy_results = await vacancy_filter.filter_vacancies(messages)

        if not vacancy_results:
            logger.error("❌ Failed to filter vacancies")
            return

        # Rank and filter final results
        top_vacancies = vacancy_filter.rank_and_filter_vacancies(vacancy_results)

        # Send results
        if not args.dry_run:
            await vacancy_filter.send_results(top_vacancies, args.target_user, messages)
        else:
            logger.info("🧪 Dry run mode - results not sent")
            print("\n" + vacancy_filter.format_vacancy_message(top_vacancies, messages))

        logger.info("✅ Vacancy filtering completed successfully")

    except Exception as e:
        logger.error(f"❌ Vacancy filtering failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
