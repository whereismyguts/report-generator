#!/usr/bin/env python3
"""
Telegram log retriever
Fetches messages from Telegram and stores them for report generation
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path

from ks_reporter.common.telegram import TelegramClientBase
from ks_reporter.common.data_manager import DataManager

logger = logging.getLogger(__name__)


class TelegramLogRetriever:
    """Retrieves and stores logs from Telegram channels"""

    def __init__(self, session_name: str = 'session-3'):
        self.telegram_client = TelegramClientBase(session_name)
        self.channel_id = os.getenv('TELEGRAM_CHANNEL_ID')  # channel username or id

        if not self.channel_id:
            raise ValueError("❌ Missing TELEGRAM_CHANNEL_ID environment variable")

        self.data_manager = DataManager()
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)

    async def fetch_messages(self, month: str) -> List[Dict]:
        """Fetch messages from Telegram channel for specified period"""
        logger.info(f"🔄 Fetching messages for {month} from channel {self.channel_id}")

        try:
            await self.telegram_client.client.start(phone=self.telegram_client.phone)

            # Resolve channel entity
            try:
                channel_entity = await self.telegram_client.client.get_entity(int(self.channel_id))
            except ValueError:
                # Try as username if not a number
                channel_entity = await self.telegram_client.client.get_entity(self.channel_id)

            # Calculate date range
            start_date = datetime.strptime(month, '%Y-%m')
            # end_date = datetime(start_date.year, start_date.month + 1, 1)
            end_date = datetime.now()

            # Adjust for year boundary
            if start_date.month == 12:
                end_date = datetime(start_date.year + 1, 1, 1)

            # ensure start_date is timezone-aware (UTC)
            start_date = start_date.replace(tzinfo=None)

            messages = []

            async for message in self.telegram_client.client.iter_messages(
                channel_entity,
                reverse=True
            ):
                # Check if message is within target month
                msg_date_naive = message.date.replace(tzinfo=None)
                if msg_date_naive < start_date or msg_date_naive >= end_date:
                    continue

                if message.text:
                    msg_data = {
                        'id': message.id,
                        'date': message.date.isoformat(),
                        'text': message.text,
                        'sender_id': message.sender_id,
                        'is_forwarded': message.fwd_from is not None
                    }
                    messages.append(msg_data)

            logger.info(f"✅ Fetched {len(messages)} messages")
            return messages

        except Exception as e:
            logger.error(f"❌ Error fetching messages: {e}")
            raise
        finally:
            await self.telegram_client.disconnect()

    def save_raw_data(self, messages: List[Dict], month: str) -> str:
        """Save raw Telegram messages to JSON file"""
        filepath = self.data_dir / f"raw_messages_{month}.json"

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)

        logger.info(f"💾 Saved raw data to {filepath}")
        return str(filepath)

    async def retrieve_monthly_logs(self, month: Optional[str] = None) -> str:
        """Main method to retrieve and save monthly logs"""
        if not month:
            month = datetime.now().strftime('%Y-%m')

        messages = await self.fetch_messages(month)
        filepath = self.save_raw_data(messages, month)

        return filepath
