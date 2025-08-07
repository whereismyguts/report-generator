#!/usr/bin/env python3
"""
Data management utilities
Provides classes for data persistence and management
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class DataManager:
    """Utility class for data persistence and management"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
    
    def save_json(self, data: Any, filename: str) -> str:
        """Save data as JSON file"""
        filepath = self.data_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        logger.info(f"💾 Saved data to {filepath}")
        return str(filepath)
    
    def load_json(self, filename: str) -> Optional[Dict]:
        """Load JSON data from file"""
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            logger.error(f"❌ File not found: {filepath}")
            return None
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to decode JSON from {filepath}: {e}")
            return None
    
    def load_resume_config(self, filepath: str = "resume.json") -> Optional[Dict]:
        """Load resume configuration"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"❌ Failed to load resume config from {filepath}: {e}")
            return None
    
    def get_last_check_timestamp(self, filename: str = "last_vacancy_check.json") -> Optional[datetime]:
        """Get timestamp of last vacancy check"""
        data = self.load_json(filename)
        if data and 'last_check' in data:
            return datetime.fromisoformat(data['last_check'])
        return None
    
    def save_last_check_timestamp(self, timestamp: datetime, filename: str = "last_vacancy_check.json"):
        """Save timestamp of last vacancy check"""
        data = {'last_check': timestamp.isoformat()}
        self.save_json(data, filename)
