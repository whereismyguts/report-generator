# shared common utilities for ks projects
try:
	from .schema import ReportData
except ImportError:
	ReportData = None
from .data_manager import DataManager
from .logging import setup_logging
from .llm_client import AIAPIClient
from .telegram_adapter import TelegramClientBase
