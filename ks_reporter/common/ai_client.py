#!/usr/bin/env python3
"""
AI API client implementations
Provides utilities for interacting with AI APIs
"""

import os
import json
import logging
import requests
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class AIAPIClient:
    """Client for AI API calls (OpenRouter, etc.)"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("❌ Missing OPENROUTER_API_KEY environment variable")
    
    def call_ai_api(self, prompt: str, model: str = "google/gemini-2.0-flash-001", temperature: float = 0.1) -> requests.Response:
        """Make API call to AI service"""
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
            },
            json={
                "model": model,
                "temperature": temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            timeout=30
        )
        
        logger.info(f"AI API call - Status: {response.status_code}")
        if response.status_code != 200:
            logger.error(f"AI API error: {response.text}")
            
        return response
    
    def extract_json_from_response(self, response: requests.Response) -> Optional[Dict]:
        """Extract and parse JSON from AI response"""
        if response.status_code != 200:
            return None
            
        try:
            result_json = response.json()
            content = result_json.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # Find JSON boundaries
            start = content.find('{')
            end = content.rfind('}')
            
            if start != -1 and end != -1:
                json_content = content[start:end + 1]
                return json.loads(json_content)
                
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error(f"❌ Failed to extract JSON from response: {e}")
            
        return None
