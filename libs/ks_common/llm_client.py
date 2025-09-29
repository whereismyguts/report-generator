import os
import json
import requests
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class AIAPIClient:
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError('Missing OPENROUTER_API_KEY')

    def call_ai_api(self, prompt: str, model: str = 'google/gemini-2.5-flash-lite', temperature: float = 0.1) -> requests.Response:
        response = requests.post(
            url='https://openrouter.ai/api/v1/chat/completions',
            headers={'Authorization': f'Bearer {self.api_key}'},
            json={'model': model, 'temperature': temperature, 'messages': [{'role': 'user', 'content': prompt}]},
            timeout=30
        )
        logger.info(f'AI API call status: {response.status_code}')
        return response

    def extract_json_from_response(self, response: requests.Response) -> Optional[Dict]:
        if response.status_code != 200:
            return None
        try:
            result_json = response.json()
            content = result_json.get('choices', [{}])[0].get('message', {}).get('content', '')
            start = content.find('{')
            end = content.rfind('}')
            if start != -1 and end != -1:
                return json.loads(content[start:end+1])
        except Exception as e:
            logger.error(f'Failed to extract JSON: {e}')
        return None
