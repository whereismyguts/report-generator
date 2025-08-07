#!/usr/bin/env python3
"""
Report generation pipeline script
Generates monthly activity reports from Telegram messages
"""

import os
import asyncio
import argparse
import logging
from pathlib import Path

from ks_reporter.common.utils import setup_logging, validate_environment
from ks_reporter.report.retriever import TelegramLogRetriever
from ks_reporter.report.generator import ReportGenerator
from ks_reporter.report.formatter import ReportFormatter
from ks_reporter.report.sender import TelegramSender

logger = logging.getLogger(__name__)


async def run_fetch(month, data_dir, session_name):
    """Fetch messages for the given month"""
    logger.info(f"🔄 Fetching messages for {month}")
    retriever = TelegramLogRetriever(session_name)
    retriever.data_dir = Path(data_dir)
    filepath = await retriever.retrieve_monthly_logs(month)
    return filepath


async def run_generate(month, prompt_path, raw_messages_path, output_path):
    """Generate report data from raw messages"""
    logger.info(f"🤖 Generating report data for {month}")
    generator = ReportGenerator()
    output_path, content = generator.generate_report_data(prompt_path, raw_messages_path, output_path)
    return output_path, content


def run_excel(json_path, reports_dir, month):
    """Generate Excel report from JSON data"""
    logger.info(f"📊 Creating Excel report for {month}")
    formatter = ReportFormatter(reports_dir)
    data = formatter.load_json_data(json_path)

    if not data:
        raise Exception("No report data loaded")

    excel_path = formatter.create_excel_report(data)
    return excel_path


async def run_send(month, excel_path, json_path, session_name, target_user, channel_id, reports_dir):
    """Send report to Telegram"""
    logger.info(f"📨 Sending report for {month}")
    sender = TelegramSender(
        session_name=session_name,
        target_user=target_user,
        channel_id=channel_id,
        reports_dir=reports_dir
    )
    success = await sender.send_monthly_report(month, excel_path, json_path)
    return success


async def main():
    """Run the full report generation pipeline"""
    parser = argparse.ArgumentParser(description="Generate and send monthly activity reports")
    parser.add_argument('--month', required=True, help='Month in YYYY-MM format')
    parser.add_argument('--session', default='session-3', help='Telegram session name')
    parser.add_argument('--target-user', type=int, default=258610595, help='Target user ID')
    parser.add_argument('--channel-id', help='Target channel ID')
    parser.add_argument('--data-dir', default='data', help='Directory for raw and processed data')
    parser.add_argument('--reports-dir', default='reports', help='Directory for reports')
    parser.add_argument('--prompt-path', default='report-prompt-v2.md', help='Prompt file path')

    args = parser.parse_args()

    # Setup logging
    setup_logging("report_generator.log")

    # Validate environment variables
    validate_environment()

    month = args.month
    session_name = args.session
    target_user = args.target_user
    channel_id = args.channel_id
    data_dir = args.data_dir
    reports_dir = args.reports_dir
    prompt_path = args.prompt_path

    logger.info(f"🚀 Running report pipeline for month: {month}")

    raw_messages_path = f'{data_dir}/raw_messages_{month}.json'
    report_json_path = f'{data_dir}/report_data_{month}.json'

    try:
        # 1. Fetch messages
        await run_fetch(month, data_dir, session_name)

        # 2. Generate report data
        _, report_content = await run_generate(month, prompt_path, raw_messages_path, report_json_path)

        # 3. Generate Excel report
        excel_path = run_excel(report_json_path, reports_dir, month)

        # 4. Send report
        await run_send(month, excel_path, report_json_path, session_name, target_user, channel_id, reports_dir)

        # 5. Send days to fill
        days_to_fill = report_content.get('days-to-fill', [])
        if days_to_fill:
            msg = f"📅 Days to fill for {month}:\n" + '\n'.join(days_to_fill)
            sender = TelegramSender(
                session_name=session_name,
                target_user=target_user,
                channel_id=channel_id,
                reports_dir=reports_dir
            )
            await sender.send_text_message(msg)
            logger.info("✅ Sent days to fill message")
        else:
            logger.info("✅ No days to fill found")

        logger.info("✅ Report pipeline completed successfully")

    except Exception as e:
        logger.error(f"❌ Report pipeline failed: {e}")
        # Send error notification
        try:
            sender = TelegramSender(
                session_name=session_name,
                target_user=target_user,
                channel_id=channel_id,
                reports_dir=reports_dir
            )
            await sender.send_error_notification(str(e), month)
        except Exception:
            pass  # Ignore errors in error notification
        raise


if __name__ == "__main__":
    asyncio.run(main())
