#!/usr/bin/env python3
"""
Telegram vacancy filter
Monitors job channels and filters vacancies based on resume
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

from ks_reporter.common.telegram import TelegramClientBase
from ks_reporter.common.ai_client import AIAPIClient
from ks_reporter.common.data_manager import DataManager
from ks_reporter.common.link_extractor import LinkExtractor
from ks_reporter.report.sender import TelegramSender

logger = logging.getLogger(__name__)


class VacancyFilter:
    """Main class for vacancy filtering and processing"""
    
    def __init__(self, session_name: str = 'session-3'):
        self.telegram_client = TelegramClientBase(session_name)
        self.ai_client = AIAPIClient()
        self.data_manager = DataManager()
        self.link_extractor = LinkExtractor()
        self.session_name = session_name
        
        # Load configuration
        self.resume_config = self.data_manager.load_resume_config()
        if not self.resume_config:
            raise ValueError("❌ Failed to load resume configuration")
            
        # Job channel IDs (will be populated from user selection)
        self.job_channels = []
    
    async def discover_channels(self) -> List[Dict]:
        """Discover and list all available channels"""
        logger.info("🔍 Discovering Telegram channels...")
        
        try:
            dialogs = await self.telegram_client.get_dialogs()
            
            # Filter for channels only
            channels = [d for d in dialogs if d['is_channel']]
            
            logger.info(f"📱 Found {len(channels)} channels:")
            for i, channel in enumerate(channels, 1):
                unread = f"({channel['unread_count']} unread)" if channel['unread_count'] > 0 else ""
                username = f"@{channel['username']}" if channel['username'] else ""
                logger.info(f"{i:2d}. {channel['title']} {username} {unread}")
                logger.info(f"     ID: {channel['id']}")
            
            return channels
            
        except Exception as e:
            logger.error(f"❌ Failed to discover channels: {e}")
            return []
        finally:
            await self.telegram_client.disconnect()
    
    def select_job_channels(self, channels: List[Dict], channel_ids: Optional[List[int]] = None) -> List[Dict]:
        """Select job-related channels from the list"""
        if channel_ids:
            # Use provided channel IDs
            selected = [ch for ch in channels if ch['id'] in channel_ids]
        else:
            # Auto-detect job channels based on keywords
            job_keywords = [
                'job', 'вакансии', 'работа', 'карьера', 'vacancy', 'hire', 'recruit',
                'python', 'developer', 'программист', 'разработчик', 'it'
            ]
            
            selected = []
            for channel in channels:
                title_lower = channel['title'].lower()
                if any(keyword in title_lower for keyword in job_keywords):
                    selected.append(channel)
        
        logger.info(f"🎯 Selected {len(selected)} job channels:")
        for channel in selected:
            logger.info(f"  - {channel['title']} (ID: {channel['id']})")
            
        return selected
    
    async def fetch_new_messages(self, hours_back: int = 24) -> List[Dict]:
        """Fetch new messages from selected job channels"""
        logger.info(f"📥 Fetching messages from last {hours_back} hours...")
        
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        all_messages = []
        
        try:
            await self.telegram_client.client.start(phone=self.telegram_client.phone)
            
            for channel in self.job_channels:
                channel_id = channel['id']
                logger.info(f"📨 Fetching from {channel['title']}...")
                
                # Fetch more messages without strict offset_date to get broader range
                messages = await self.telegram_client.fetch_messages_from_channel(
                    channel_id, 
                    limit=500,  # Increased limit to get more messages
                    offset_date=None  # Remove strict date filtering at fetch level
                )
                
                # Filter messages by time after fetching
                new_messages = []
                for msg in messages:
                    try:
                        # Parse message date more robustly
                        msg_date_str = msg['date']
                        if msg_date_str.endswith('Z'):
                            msg_date_str = msg_date_str[:-1] + '+00:00'
                        
                        msg_date = datetime.fromisoformat(msg_date_str).replace(tzinfo=None)
                        
                        # Check if message is within our time window
                        if msg_date > cutoff_time:
                            new_messages.append(msg)
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to parse date for message {msg.get('id', 'unknown')}: {e}")
                        # Include message anyway if we can't parse the date
                        new_messages.append(msg)
                
                logger.info(f"  📊 Found {len(new_messages)} new messages (out of {len(messages)} total)")
                all_messages.extend(new_messages)
            
            logger.info(f"📈 Total new messages: {len(all_messages)}")
            return all_messages
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch messages: {e}")
            return []
        finally:
            await self.telegram_client.disconnect()
    
    def prepare_ai_prompt(self, messages: List[Dict]) -> str:
        """Prepare prompt for AI vacancy filtering"""
        # Load prompt template
        try:
            with open('vacancy-filter-prompt.md', 'r', encoding='utf-8') as f:
                prompt_template = f.read()
        except FileNotFoundError:
            logger.error("❌ Vacancy filter prompt file not found")
            return ""
        
        # Insert resume content using safe replacement
        resume_content = json.dumps(self.resume_config, indent=2, ensure_ascii=False)
        prompt = prompt_template.replace('{resume_content}', resume_content)
        
        # Add messages data
        messages_json = json.dumps(messages, indent=2, ensure_ascii=False)
        prompt += f"\n\n**VACANCY MESSAGES TO ANALYZE:**\n\n{messages_json}"
        
        return prompt
    
    async def filter_vacancies(self, messages: List[Dict]) -> Optional[Dict]:
        """Filter vacancies using AI"""
        if not messages:
            logger.info("📭 No messages to filter")
            return None
            
        logger.info(f"🤖 Filtering {len(messages)} messages with AI...")
        
        # Prepare prompt
        prompt = self.prepare_ai_prompt(messages)
        
        # Process links in messages
        await self._process_message_links(messages)
        
        # Make AI API call
        response = self.ai_client.call_ai_api(prompt)
        result = self.ai_client.extract_json_from_response(response)
        
        if result:
            vacancies = result.get('vacancies', [])
            logger.info(f"✅ AI found {len(vacancies)} matching vacancies")
            
            # Save raw results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.data_manager.save_json(result, f"vacancy_results_{timestamp}.json")
            
            return result
        else:
            logger.error("❌ Failed to get valid response from AI")
            return None
    
    async def _process_message_links(self, messages: List[Dict]):
        """Process and extract additional content from links in messages"""
        for message in messages:
            # Extract URLs from text
            urls = self.link_extractor.extract_urls_from_text(message['text'])
            
            # Extract Telegram links
            tg_links = self.link_extractor.extract_telegram_links(message['text'])
            
            # Store extracted links
            message['extracted_urls'] = urls
            message['telegram_links'] = tg_links
            
            # For now, just log the links. In the future, could fetch content
            if urls or tg_links:
                logger.debug(f"📎 Message {message['id']} has links: {urls + tg_links}")
    
    def rank_and_filter_vacancies(self, vacancy_results: Dict) -> List[Dict]:
        """Final ranking and filtering of vacancies"""
        vacancies = vacancy_results.get('vacancies', [])
        
        if not vacancies:
            return []
        
        # Sort by score (highest first)
        sorted_vacancies = sorted(vacancies, key=lambda x: x.get('score', 0), reverse=True)
        
        # Filter by minimum score and recommendation
        min_score = self.resume_config.get('scoring_weights', {}).get('min_score', 0.4)
        good_recommendations = ['apply', 'consider']
        
        filtered_vacancies = [
            v for v in sorted_vacancies 
            if v.get('score', 0) >= min_score and 
            v.get('recommendation', '').lower() in good_recommendations
        ]
        
        # Limit to top N vacancies
        max_vacancies = 10
        top_vacancies = filtered_vacancies[:max_vacancies]
        
        logger.info(f"🏆 Final selection: {len(top_vacancies)} top vacancies")
        
        return top_vacancies
    
    def format_vacancy_message(self, vacancies: List[Dict]) -> str:
        """Format vacancy results for Telegram message"""
        if not vacancies:
            return "📭 No matching vacancies found in recent messages."
        
        message = f"🎯 **Found {len(vacancies)} matching vacancies!**\n\n"
        
        for i, vacancy in enumerate(vacancies, 1):
            score = vacancy.get('score', 0)
            title = vacancy.get('title', 'Unknown Title')
            company = vacancy.get('company', 'Unknown Company')
            location = vacancy.get('location', 'Unknown Location')
            salary = vacancy.get('salary', 'Not specified')
            recommendation = vacancy.get('recommendation', 'consider')
            
            emoji = "🔥" if recommendation == "apply" else "💼"
            
            message += f"{emoji} **{i}. {title}**\n"
            message += f"🏢 {company}\n"
            message += f"📍 {location}\n"
            message += f"💰 {salary}\n"
            message += f"📊 Score: {score:.2f}\n"
            
            # Add match reasons
            reasons = vacancy.get('match_reasons', [])
            if reasons:
                message += f"✅ **Matches:** {', '.join(reasons[:2])}\n"
            
            # Add concerns if any
            concerns = vacancy.get('concerns', [])
            if concerns:
                message += f"⚠️ **Concerns:** {', '.join(concerns[:1])}\n"
            
            message += "\n"
        
        message += f"📊 Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        return message
    
    async def send_results(self, vacancies: List[Dict], target_user: int):
        """Send filtered vacancy results to user"""
        if not vacancies:
            logger.info("📭 No vacancies to send")
            return False
        
        message = self.format_vacancy_message(vacancies)
        
        sender = TelegramSender(
            session_name=self.session_name,
            target_user=target_user,
            channel_id=None,
            reports_dir='data'
        )
        
        success = await sender.send_text_message(message)
        
        if success:
            logger.info("✅ Vacancy results sent successfully")
        else:
            logger.error("❌ Failed to send vacancy results")
            
        return success
