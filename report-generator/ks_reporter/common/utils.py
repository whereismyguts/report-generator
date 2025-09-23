#!/usr/bin/env python3
"""
Common utility functions
Provides shared utility functions across modules
"""

import os
import logging
from pathlib import Path


def setup_logging(log_file: str = "application.log", level: int = logging.INFO):
    """Setup logging configuration"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / log_file),
            logging.StreamHandler()
        ]
    )


def validate_environment():
    """Validate that all required environment variables are set"""
    required_vars = [
        'TELEGRAM_API_ID',
        'TELEGRAM_API_HASH',
        'TELEGRAM_PHONE',
        'OPENROUTER_API_KEY'
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        raise ValueError(f"❌ Missing required environment variables: {missing_vars}")

    logger = logging.getLogger(__name__)
    logger.info("✅ Environment validation passed")
