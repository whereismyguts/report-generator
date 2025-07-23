#!/usr/bin/env python3
"""
Full pipeline runner for report generation and delivery
"""
import os
import datetime
import asyncio
import argparse
from pathlib import Path
import logging

from telegram_retriever import TelegramLogRetriever
import report_v2
from generate_report_data import openrouter_call, process_days
from telegram_sender import TelegramSender


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pipeline")


def run_fetch(month, data_dir):
    retriever = TelegramLogRetriever()
    retriever.data_dir = Path(data_dir)
    loop = asyncio.get_event_loop()
    filepath = loop.run_until_complete(retriever.retrieve_monthly_logs(month))
    return filepath


def run_generate(month, prompt_path, raw_messages_path, output_path):
    import json

    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompt = f.read()

    with open(raw_messages_path, 'r', encoding='utf-8') as f:
        history_json = json.load(f)

    message = prompt + '\n\n' + json.dumps(history_json, indent=2, ensure_ascii=False)
    response = openrouter_call(message)

    if response.status_code == 200:
        result_json = response.json()
        content = result_json.get('choices', [{}])[0].get('message', {}).get('content', '')
        start = content.find('{')
        end = content.rfind('}')
        if start != -1 and end != -1:
            content = content[start:end + 1]
        content = json.loads(content)

        content = process_days(content, month)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)

        return output_path, content
    else:
        logger.error(f"Error: {response.status_code} - {response.reason}")
        logger.error(f"Response content: {response.text}")
        raise Exception("Report generation failed")


def run_excel(json_path, reports_dir, month):
    data = report_v2.load_json_data(json_path)
    if not data:
        raise Exception("No report data loaded")
    first_day = data.get('days', [{}])[0].get('date', 'unknown')
    month_str, year = first_day.split('-')[:2]

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    output_xls_filename = Path(reports_dir) / f"Anton_Karmanov_{month_str}_{year}_v{timestamp}.xlsx"

    os.makedirs(reports_dir, exist_ok=True)
    report_v2.create_xls_from_json(data, str(output_xls_filename))
    return str(output_xls_filename)


def run_send(month, excel_path, json_path, session_name, target_user, channel_id, reports_dir):
    sender = TelegramSender(
        session_name=session_name,
        target_user=target_user,
        channel_id=channel_id,
        reports_dir=reports_dir
    )
    loop = asyncio.get_event_loop()
    success = loop.run_until_complete(sender.send_monthly_report(month, excel_path, json_path))
    return success


def main():
    parser = argparse.ArgumentParser(description="Run full report pipeline")
    parser.add_argument('--month', required=True, help='Month in YYYY-MM format')
    parser.add_argument('--session', default='session-3', help='Telegram session name')
    parser.add_argument('--target-user', type=int, default=258610595, help='Target user id')
    parser.add_argument('--channel-id', help='Target channel id')
    parser.add_argument('--data-dir', default='data', help='Directory for raw and processed data')
    parser.add_argument('--reports-dir', default='reports', help='Directory for reports')
    parser.add_argument('--prompt-path', default='report-prompt-v2.md', help='Prompt file path')
    args = parser.parse_args()

    month = args.month
    session_name = args.session
    target_user = args.target_user
    channel_id = args.channel_id
    data_dir = args.data_dir
    reports_dir = args.reports_dir
    prompt_path = args.prompt_path
    logger.info(f"Running full pipeline for month: {month}, session: {session_name}, target user: {target_user}, channel id: {channel_id}")
    raw_messages_path = f'{data_dir}/raw_messages_{month}.json'
    report_json_path = f'{data_dir}/report_data_{month}.json'

    # 1. Fetch messages
    logger.info(f"Step 1: Fetching messages for {month}")
    run_fetch(month, data_dir)

    # 2. Generate report data
    logger.info(f"Step 2: Generating report data for {month}")
    _, report_content = run_generate(month, prompt_path, raw_messages_path, report_json_path)

    # 3. Generate Excel report
    logger.info(f"Step 3: Generating Excel report for {month}")
    excel_path = run_excel(report_json_path, reports_dir, month)

    # 4. Send report and days to fill
    logger.info(f"Step 4: Sending report to user {target_user}")
    run_send(month, excel_path, report_json_path, session_name, target_user, channel_id, reports_dir)

    # 5. Send days to fill
    days_to_fill = report_content.get('days-to-fill', [])
    if days_to_fill:
        msg = f"Days to fill for {month}:\n" + '\n'.join(days_to_fill)
        sender = TelegramSender(
            session_name=session_name,
            target_user=target_user,
            channel_id=channel_id,
            reports_dir=reports_dir
        )
        loop = asyncio.get_event_loop()
        loop.run_until_complete(sender.send_text_message(msg))
        logger.info("Sent days to fill message.")
    else:
        logger.info("No days to fill.")


if __name__ == '__main__':
    main()
