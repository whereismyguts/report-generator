#!/usr/bin/env python3
"""
Report generator
Generates structured report data from raw logs using AI
"""

import json
import logging
from typing import Dict, Tuple, Optional

from ks_reporter.common.ai_client import AIAPIClient
from ks_reporter.common.data_manager import DataManager

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates report data from raw logs using AI"""
    
    def __init__(self):
        self.ai_client = AIAPIClient()
        self.data_manager = DataManager()
    
    def generate_report_data(self, prompt_path: str, raw_messages_path: str, output_path: str) -> Tuple[str, Dict]:
        """Generate report data from raw messages using AI"""
        logger.info(f"🤖 Generating report data using prompt {prompt_path}")
        
        try:
            # Load prompt template
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt = f.read()
                
            # Load raw messages
            with open(raw_messages_path, 'r', encoding='utf-8') as f:
                history_json = json.load(f)
                
            # Create full prompt
            message = prompt + '\n\n' + json.dumps(history_json, indent=2, ensure_ascii=False)
            
            # Call AI API
            response = self.ai_client.call_ai_api(message)
            
            if response.status_code == 200:
                # Extract and parse JSON response
                content = self.ai_client.extract_json_from_response(response)
                
                if not content:
                    logger.error("❌ Failed to extract valid JSON from AI response")
                    raise Exception("Report generation failed: Invalid response format")
                
                # Process days (add any post-processing here)
                # Extract month from the data for processing
                month_for_processing = None
                if 'days' in content and content['days']:
                    first_date = content['days'][0].get('date', '')
                    if first_date:
                        month_for_processing = first_date[:7]  # YYYY-MM format
                
                content = self._process_days(content, month_for_processing)
                
                # Save output
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(content, f, indent=2, ensure_ascii=False)
                    
                logger.info(f"✅ Report data generated and saved to {output_path}")
                return output_path, content
                
            else:
                logger.error(f"❌ API error: {response.status_code} - {response.text}")
                raise Exception(f"Report generation failed: API error {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Report generation error: {e}")
            raise
    
    def _process_days(self, content: Dict, month: Optional[str] = None) -> Dict:
        """Process days in the report content - same logic as working example"""
        import datetime
        from typing import Union
        
        if not month:
            # Try to extract month from content or use current
            if 'days' in content and content['days']:
                first_date = content['days'][0].get('date', '')
                if first_date:
                    month = first_date[:7]  # YYYY-MM format
        
        if isinstance(month, str):
            month_obj = datetime.datetime.strptime(month, '%Y-%m').date()
        else:
            month_obj = month
            
        if not month_obj:
            return content

        days_to_fill = []
        for day in content.get('not-mentioned-days', []):
            date_obj = datetime.datetime.strptime(day, '%Y-%m-%d').date()
            if date_obj.weekday() >= 5:  # Saturday or Sunday
                print(f" - Weekend date: {day}")
                continue

            if date_obj.month != month_obj.month or date_obj.year != month_obj.year:
                print(f" - Out of month date: {day}")
                continue

            print(f" Working day to fill: {day}")
            days_to_fill.append(day)

        days = []
        for day in content.get('days', []):
            date_obj = datetime.datetime.strptime(day['date'], '%Y-%m-%d').date()
            if date_obj.month != month_obj.month or date_obj.year != month_obj.year:
                print(f" - Skipping day out of month: {day['date']}")
                continue
            days.append(day)

        content['days-to-fill'] = days_to_fill
        content['days'] = days
        return content
