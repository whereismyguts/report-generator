import logging
from pathlib import Path


def setup_logging(log_file: str = 'application.log', level: int = logging.INFO):
    Path('logs').mkdir(exist_ok=True)
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(Path('logs') / log_file),
            logging.StreamHandler()
        ]
    )

    return logging.getLogger()
