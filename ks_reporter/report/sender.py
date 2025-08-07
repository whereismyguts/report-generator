#!/usr/bin/env python3
"""
Telegram sender
Sends generated reports back to Telegram
"""

import os
import asyncio
from datetime import datetime
from pathlib import Path
import logging
from typing import Optional

from ks_reporter.common.telegram import TelegramClientBase

logger = logging.getLogger(__name__)


class TelegramSender:
    """Telegram sender for reports and notifications"""

    def __init__(self, session_name: str = 'session-3', target_user: int = None,
                 channel_id: Optional[int] = None, reports_dir: str = 'reports'):
        self.telegram_client = TelegramClientBase(session_name)
        self.target_user = target_user
        self.channel_id = channel_id
        self.reports_dir = Path(reports_dir)

    async def send_text_message(self, message: str) -> bool:
        """Send a text message to the target user or channel"""
        if not message:
            logger.error("❌ Empty message, not sending")
            return False

        try:
            await self.telegram_client.client.start(phone=self.telegram_client.phone)

            # Determine recipient (user or channel)
            recipient = self.channel_id if self.channel_id else self.target_user

            if not recipient:
                logger.error("❌ No recipient (target_user or channel_id) specified")
                return False

            # Send the message
            logger.info(f"📨 Sending message to {recipient}")
            await self.telegram_client.client.send_message(recipient, message)

            return True

        except Exception as e:
            logger.error(f"❌ Failed to send message: {e}")
            return False
        finally:
            await self.telegram_client.disconnect()

    async def send_file(self, filepath: str, caption: Optional[str] = None) -> bool:
        """Send a file to the target user or channel"""
        if not os.path.exists(filepath):
            logger.error(f"❌ File not found: {filepath}")
            return False

        try:
            await self.telegram_client.client.start(phone=self.telegram_client.phone)

            # Determine recipient (user or channel)
            recipient = self.channel_id if self.channel_id else self.target_user

            if not recipient:
                logger.error("❌ No recipient (target_user or channel_id) specified")
                return False

            # Send the file
            logger.info(f"📎 Sending file {filepath} to {recipient}")
            await self.telegram_client.client.send_file(recipient, filepath, caption=caption)

            return True

        except Exception as e:
            logger.error(f"❌ Failed to send file: {e}")
            return False
        finally:
            await self.telegram_client.disconnect()

    async def send_monthly_report(self, month: str, excel_path: str, json_path: str) -> bool:
        """Send monthly report files with a caption"""
        caption = f"📊 Monthly Report for {month}"

        # First send Excel file
        excel_success = await self.send_file(excel_path, caption)

        # Then send JSON data if needed
        # json_success = await self.send_file(json_path, "📋 Report raw data")

        return excel_success

    async def send_error_notification(self, error_message: str, month: str = None) -> bool:
        """Send error notification"""
        period = f" for {month}" if month else ""
        message = f"❌ **ERROR: Report Generation{period} Failed**\n\n{error_message}"
        return await self.send_text_message(message)
