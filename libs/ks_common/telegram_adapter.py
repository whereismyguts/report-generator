import os
import logging
from telethon import TelegramClient

logger = logging.getLogger(__name__)


class TelegramClientBase:
    def __init__(self, session_name: str = 'session-3'):
        self.api_id = int(os.getenv('TELEGRAM_API_ID') or 0)
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.phone = os.getenv('TELEGRAM_PHONE')
        if not (self.api_id and self.api_hash and self.phone):
            raise ValueError('Missing telegram credentials')
        self.client = TelegramClient(session_name, self.api_id, self.api_hash)

    async def start(self):
        await self.client.start(phone=self.phone)

    async def disconnect(self):
        await self.client.disconnect()

    async def send_message(self, recipient, message):
        await self.client.send_message(recipient, message)

    async def send_file(self, recipient, path, caption=None):
        await self.client.send_file(recipient, path, caption=caption)
