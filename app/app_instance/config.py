import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Config:
    TELEGRAM_LOGGER_BOT_TOKEN = os.getenv('TELEGRAM_LOGGER_BOT_TOKEN')
    TELEGRAM_LOG_RECEIVERS = os.getenv('TELEGRAM_LOG_RECEIVERS').split(',')

    DEBUG = bool(int(os.getenv('DEBUG', 0)))


class FilePaths:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
