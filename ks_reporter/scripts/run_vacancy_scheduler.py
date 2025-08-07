#!/usr/bin/env python3
"""
Vacancy scheduler script
Runs vacancy filtering on a schedule
"""

import asyncio
import argparse
import logging

from ks_reporter.common.utils import setup_logging, validate_environment
from ks_reporter.vacancy.scheduler import VacancyScheduler

logger = logging.getLogger(__name__)


async def run_once(args):
    """Run vacancy check once and exit"""
    scheduler = VacancyScheduler(
        session_name=args.session,
        target_user=args.target_user
    )
    await scheduler.run_vacancy_check()


def run_continuously(args):
    """Run scheduler continuously"""
    scheduler = VacancyScheduler(
        session_name=args.session,
        target_user=args.target_user
    )
    scheduler.run_forever()


async def main():
    """Main entry point for scheduler"""
    parser = argparse.ArgumentParser(description="Automated vacancy scheduler")
    parser.add_argument('--session', default='session-3', help='Telegram session name')
    parser.add_argument('--target-user', type=int, default=258610595, help='Target user ID')
    parser.add_argument('--once', action='store_true', help='Run once instead of continuously')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon (background)')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.INFO if not args.daemon else logging.WARNING
    setup_logging("vacancy_scheduler.log", log_level)
    
    # Validate environment
    validate_environment()
    
    try:
        if args.once:
            logger.info("🔄 Running vacancy check once")
            await run_once(args)
            logger.info("✅ Vacancy check completed")
        else:
            logger.info("🚀 Starting continuous vacancy scheduler")
            # This doesn't return as it runs forever
            run_continuously(args)
            
    except Exception as e:
        logger.error(f"❌ Scheduler failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
