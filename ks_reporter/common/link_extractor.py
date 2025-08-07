#!/usr/bin/env python3
"""
Link processing utilities
Provides utilities for extracting and processing links from messages
"""

import logging
import requests
from typing import List, Optional

logger = logging.getLogger(__name__)


class LinkExtractor:
    """Utility for extracting and processing links from messages"""
    
    @staticmethod
    def extract_urls_from_text(text: str) -> List[str]:
        """Extract URLs from text using regex"""
        import re
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, text)
    
    @staticmethod
    def extract_telegram_links(text: str) -> List[str]:
        """Extract Telegram-specific links (t.me, @username)"""
        import re
        patterns = [
            r't\.me/[a-zA-Z0-9_]+',
            r'@[a-zA-Z0-9_]+',
            r'tg://[a-zA-Z0-9_/?=&]+'
        ]
        
        links = []
        for pattern in patterns:
            links.extend(re.findall(pattern, text))
            
        return links
    
    def fetch_link_content(self, url: str) -> Optional[str]:
        """Fetch content from URL (basic implementation)"""
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; VacancyBot/1.0)'
            })
            
            if response.status_code == 200:
                return response.text
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to fetch content from {url}: {e}")
            
        return None
