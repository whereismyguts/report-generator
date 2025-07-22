#!/usr/bin/env python3
"""
telegram delivery service for automated reporting system
sends generated reports back to telegram channel
"""

import os
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import logging

# pip install telethon python-dotenv
try:
    from telethon import TelegramClient
    import dotenv
    dotenv.load_dotenv()
except ImportError:
    print("❌ Install required packages: pip install telethon python-dotenv")
    exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramSender:
    def __init__(self):
        # telegram api credentials from environment
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.phone = os.getenv('TELEGRAM_PHONE')
        self.channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
        
        if not all([self.api_id, self.api_hash, self.phone, self.channel_id]):
            raise ValueError("❌ missing telegram credentials in environment variables")
        
        self.client = TelegramClient('session-3', self.api_id, self.api_hash)
        self.reports_dir = Path('reports')
    
    async def send_text_message(self, message: str) -> bool:
        """send text message to telegram channel"""
        try:
            await self.client.start(phone=self.phone)
            await self.client.send_message(258610595, message)
            logger.info("✅ text message sent successfully")
            return True
        except Exception as e:
            logger.error(f"❌ failed to send text message: {e}")
            return False
        finally:
            await self.client.disconnect()
    
    async def send_file(self, filepath: str, caption: str = "") -> bool:
        """send file to telegram channel"""
        try:
            await self.client.start(phone=self.phone)
            
            file_path = Path(filepath)
            if not file_path.exists():
                logger.error(f"❌ file not found: {filepath}")
                return False
            
            await self.client.send_file(
                self.channel_id,
                str(file_path),
                caption=caption,
                force_document=True
            )
            
            logger.info(f"✅ file sent successfully: {file_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ failed to send file: {e}")
            return False
        finally:
            await self.client.disconnect()
    
    async def send_multiple_files(self, filepaths: List[str], caption: str = "") -> bool:
        """send multiple files to telegram channel"""
        try:
            await self.client.start(phone=self.phone)
            
            valid_files = []
            for filepath in filepaths:
                file_path = Path(filepath)
                if file_path.exists():
                    valid_files.append(str(file_path))
                else:
                    logger.warning(f"⚠️  file not found: {filepath}")
            
            if not valid_files:
                logger.error("❌ no valid files to send")
                return False
            
            await self.client.send_file(
                self.channel_id,
                valid_files,
                caption=caption,
                force_document=True
            )
            
            logger.info(f"✅ {len(valid_files)} files sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ failed to send files: {e}")
            return False
        finally:
            await self.client.disconnect()
    
    def generate_report_summary(self, month: str, json_filepath: str) -> str:
        """generate summary message for monthly report"""
        try:
            import json
            with open(json_filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            total_days = len(data['days'])
            total_tasks = sum(len(day['done']) for day in data['days'])
            total_hours = sum(task['duration'] for day in data['days'] for task in day['done'])
            not_mentioned = len(data['not-mentioned-days'])
            
            # calculate task type distribution
            meetings = sum(1 for day in data['days'] for task in day['done'] if task['type'] == 'meeting')
            tasks = total_tasks - meetings
            
            summary = f"""📊 **Monthly Report - {month}**

📅 **Period Summary:**
• Working days: {total_days}
• Total tasks completed: {tasks}
• Meetings attended: {meetings}
• Total hours logged: {total_hours}h
• Days not mentioned: {not_mentioned}

🏆 **Productivity Metrics:**
• Average tasks per day: {tasks/total_days:.1f}
• Average hours per day: {total_hours/total_days:.1f}h
• Task completion rate: {(total_days/(total_days+not_mentioned)*100):.1f}%

📁 **Files included:**
• Excel report with detailed breakdown
• JSON data for further analysis
• Summary statistics

Generated automatically on {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ failed to generate summary: {e}")
            return f"📊 Monthly Report - {month}\n\nGenerated on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    async def send_monthly_report(self, month: str, excel_path: str, json_path: str) -> bool:
        """send complete monthly report with summary and files"""
        logger.info(f"📤 sending monthly report for {month}")
        
        # generate summary message
        summary = self.generate_report_summary(month, json_path)
        
        # send summary first
        summary_sent = await self.send_text_message(summary)
        if not summary_sent:
            logger.error("❌ failed to send summary message")
            return False
        
        # send files
        files_to_send = []
        if Path(excel_path).exists():
            files_to_send.append(excel_path)
        if Path(json_path).exists():
            files_to_send.append(json_path)
        
        if files_to_send:
            files_sent = await self.send_multiple_files(
                files_to_send,
                f"📎 Report files for {month}"
            )
            if not files_sent:
                logger.error("❌ failed to send report files")
                return False
        
        logger.info(f"✅ monthly report sent successfully for {month}")
        return True
    
    async def send_error_notification(self, error_message: str, month: str) -> bool:
        """send error notification to telegram"""
        error_msg = f"""❌ **Report Generation Failed**

**Month:** {month}
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

**Error:** {error_message}

Please check the logs and retry manually if needed."""
        
        return await self.send_text_message(error_msg)


async def main():
    """cli interface for telegram sender"""
    import argparse
    
    parser = argparse.ArgumentParser(description='send reports to telegram')
    parser.add_argument('--month', required=True, help='month in YYYY-MM format')
    parser.add_argument('--excel', help='excel report file path')
    parser.add_argument('--json', help='json report file path')
    parser.add_argument('--message', help='custom message to send')
    
    args = parser.parse_args()
    
    sender = TelegramSender()
    
    try:
        if args.message:
            success = await sender.send_text_message(args.message)
        elif args.excel and args.json:
            success = await sender.send_monthly_report(args.month, args.excel, args.json)
        else:
            # auto-detect files
            reports_dir = Path('/home/karmanov/me/wiki/scripts/reports')
            excel_path = reports_dir / f"report-{args.month}.xlsx"
            json_path = reports_dir / f"report-data-{args.month}.json"
            
            success = await sender.send_monthly_report(args.month, str(excel_path), str(json_path))
        
        if success:
            print("✅ telegram delivery completed successfully")
        else:
            print("❌ telegram delivery failed")
            exit(1)
            
    except Exception as e:
        logger.error(f"❌ delivery failed: {e}")
        await sender.send_error_notification(str(e), args.month)
        exit(1)


if __name__ == '__main__':
    asyncio.run(main())
