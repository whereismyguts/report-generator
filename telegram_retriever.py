#!/usr/bin/env python3
"""
telegram log retrieval service for automated reporting system
fetches messages from telegram channel and stores them locally
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
import logging

# pip install telethon python-dotenv
try:
    from telethon import TelegramClient
    from telethon.tl.types import Message
    import dotenv
    dotenv.load_dotenv()
except ImportError:
    print("❌ Install required packages: pip install telethon python-dotenv")
    exit(1)

# configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    # handlers=[
    #     logging.FileHandler('.logs/telegram_retriever.log'),
    #     logging.StreamHandler()
    # ]
)
logger = logging.getLogger(__name__)


class TelegramLogRetriever:
    def __init__(self):
        # telegram api credentials from environment
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.phone = os.getenv('TELEGRAM_PHONE')
        self.channel_id = os.getenv('TELEGRAM_CHANNEL_ID')  # channel username or id

        if not all([self.api_id, self.api_hash, self.phone, self.channel_id]):
            raise ValueError("❌ missing telegram credentials in environment variables")

        self.client = TelegramClient('session-3', self.api_id, self.api_hash)
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)

    async def fetch_messages(self, month) -> List[Dict]:
        """fetch messages from telegram channel for specified period"""
        logger.info(f"🔄 fetching messages {month} from channel {self.channel_id}")

        try:
            logger.info("Starting with phone: %s", self.phone)
            await self.client.start(phone=self.phone)

            # list all channel i subscribed to
            channels = await self.client.get_dialogs()
            for channel in channels:
                if channel.is_channel:
                    logger.info(f"Channel: {channel}")
                    channel_id = channel.id
                    break

            # calculate date range

            start_date = datetime.strptime(month, '%Y-%m') - timedelta(days=1)  # start from the last day of previous month
            end_date = start_date + timedelta(days=33)  # 30 days period

            # ensure start_date is timezone-aware (UTC)
            start_date = start_date.replace(tzinfo=None)

            messages = []

            async for message in self.client.iter_messages(
                channel_id,
                reverse=True
            ):

                msg_date_naive = message.date.replace(tzinfo=None)
                if msg_date_naive < start_date or msg_date_naive >= end_date:
                    continue

                print(f"Processing message ID: {message.id}, Date: {message.date}")
                # print(f'Message: {message}')
                if message.text:
                    msg_data = {
                        'id': message.id,
                        'date': message.date.isoformat(),
                        'text': message.text,
                        'sender_id': message.sender_id,
                        'is_forwarded': message.fwd_from is not None
                    }
                    messages.append(msg_data)

            logger.info(f"✅ fetched {len(messages)} messages")
            return messages

        except Exception as e:
            logger.error(f"❌ error fetching messages: {e}")
            raise
        finally:
            await self.client.disconnect()

    def save_raw_data(self, messages: List[Dict], month: str) -> str:
        """save raw telegram messages to json file"""
        filename = f"raw_messages_{month}.json"
        filepath = self.data_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)

        logger.info(f"💾 saved {len(messages)} messages to {filepath}")
        return str(filepath)

    # def filter_work_messages(self, messages: List[Dict]) -> List[Dict]:
    #     """filter messages that contain work-related content"""
    #     work_keywords = [
    #         'done', 'todo', 'wip', 'task', 'meeting', 'integration',
    #         'deploy', 'test', 'debug', 'fix', 'api', 'auth', 'bitrix',
    #         'huntflow', 'alliance', 'farpost', 'premium', 'minzdrav'
    #     ]

    #     filtered = []
    #     for msg in messages:
    #         text_lower = msg['text'].lower()
    #         if any(keyword in text_lower for keyword in work_keywords):
    #             filtered.append(msg)

    #     logger.info(f"🔍 filtered {len(filtered)} work-related messages from {len(messages)} total")
    #     return filtered

    async def retrieve_monthly_logs(self, month: Optional[str] = None) -> str:
        """main method to retrieve and save monthly logs"""

        logger.info(f"🚀 starting log retrieval for {month}")

        # fetch messages
        messages = await self.fetch_messages(month)

        # filter work-related messages
        # work_messages = self.filter_work_messages(messages)
        work_messages = messages

        # save raw data
        filepath = self.save_raw_data(work_messages, month)

        logger.info(f"✅ monthly log retrieval completed for {month}")
        return filepath


async def main():
    """cli interface for telegram retriever"""
    import argparse

    parser = argparse.ArgumentParser(description='retrieve telegram logs')
    parser.add_argument('--month', help='month in YYYY-MM format', required=True)

    args = parser.parse_args()

    retriever = TelegramLogRetriever()

    try:
        if args.month:
            filepath = await retriever.retrieve_monthly_logs(args.month)
        else:
            messages = await retriever.fetch_messages(args.days)
            month = datetime.now().strftime('%Y-%m')
            filepath = retriever.save_raw_data(messages, month)

        print(f"✅ logs saved to: {filepath}")

    except Exception as e:
        logger.error(f"❌ retrieval failed: {e}")
        exit(1)


if __name__ == '__main__':
    asyncio.run(main())
