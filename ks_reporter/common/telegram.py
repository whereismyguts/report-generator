#!/usr/bin/env python3
"""
Base telegram client implementation
Provides common functionality for Telegram operations
"""

import os
import logging
from typing import Dict, List, Optional

# pip install telethon python-dotenv
try:
    from telethon import TelegramClient
    import dotenv
    dotenv.load_dotenv()
except ImportError:
    print("❌ Install required packages: pip install telethon python-dotenv")
    exit(1)

logger = logging.getLogger(__name__)


class TelegramClientBase:
    """Base class for Telegram client operations"""

    def __init__(self, session_name: str = 'session-3'):
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.phone = os.getenv('TELEGRAM_PHONE')

        if not all([self.api_id, self.api_hash, self.phone]):
            raise ValueError("❌ Missing telegram credentials in environment variables")

        self.client = TelegramClient(session_name, self.api_id, self.api_hash)

    async def get_dialogs(self) -> List[Dict]:
        """Get list of all channels and chats"""
        await self.client.start(phone=self.phone)
        dialogs = []

        async for dialog in self.client.iter_dialogs():
            dialog_info = {
                'id': dialog.id,
                'title': dialog.title,
                'username': getattr(dialog.entity, 'username', None),
                'is_channel': dialog.is_channel,
                'is_group': dialog.is_group,
                'is_user': dialog.is_user,
                'unread_count': dialog.unread_count
            }
            dialogs.append(dialog_info)

        return dialogs

    async def fetch_messages_from_channel(self, channel_id: int, limit: int = 100, offset_date=None) -> List[Dict]:
        """Fetch messages from a specific channel"""
        messages = []

        try:
            async for message in self.client.iter_messages(
                channel_id,
                limit=limit,
                offset_date=offset_date,
                reverse=False
            ):
                if message.text:
                    msg_data = {
                        'id': message.id,
                        'date': message.date.isoformat(),
                        'text': message.text,
                        'sender_id': message.sender_id,
                        'is_forwarded': message.fwd_from is not None,
                        'channel_id': channel_id,
                        'entities': self._extract_entities(message)
                    }
                    messages.append(msg_data)

        except Exception as e:
            logger.error(f"❌ Error fetching messages from channel {channel_id}: {e}")

        return messages

    def _extract_entities(self, message) -> List[Dict]:
        """Extract URLs and other entities from message"""
        entities = []
        if hasattr(message, 'entities') and message.entities:
            for entity in message.entities:
                entity_info = {
                    'type': type(entity).__name__,
                    'offset': entity.offset,
                    'length': entity.length
                }

                # Extract URL if it's a URL entity
                if hasattr(entity, 'url'):
                    entity_info['url'] = entity.url

                entities.append(entity_info)

        return entities

    async def disconnect(self):
        """Disconnect the client"""
        await self.client.disconnect()
