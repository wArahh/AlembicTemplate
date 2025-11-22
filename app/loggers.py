import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.shared.config import Config


class BaseFormatter(logging.Formatter):
    LEVEL_EMOJIS = {
        'DEBUG': '🐛',
        'INFO': 'ℹ️',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '❗❗❗'
    }

    def get_emoji(self, levelname):
        self.emoji = self.LEVEL_EMOJIS.get(levelname)
        return self.emoji


class TelegramFormatter(BaseFormatter):
    def format(self, record):
        emoji = self.get_emoji(record.levelname)
        asctime = self.formatTime(record, self.datefmt if hasattr(self, 'datefmt') else None)
        formatted = (
            f'<b>{emoji} {record.levelname}</b> <code>[{asctime}]</code>\n'
            f'<b>Module:</b> <code>{record.name}</code>\n'
            f'<b>Function:</b> <code>{record.funcName}()</code>\n'
            f'<b>Location:</b> <code>{record.filename}:{record.lineno}</code>\n\n'
            f'{record.msg}'
        )
        return formatted


class ConsoleFormatter(BaseFormatter):
    def format(self, record):
        emoji = self.get_emoji(record.levelname)
        asctime = self.formatTime(record, self.datefmt if hasattr(self, 'datefmt') else None)

        try:
            message = record.msg % record.args if record.args else record.msg
        except (TypeError, ValueError):
            message = record.msg

        formatted = (
            f'{emoji} {record.levelname} - {record.name} - [{asctime}] - {record.funcName}() - {record.filename}:{record.lineno} - {message}'
        )
        return formatted


_logger_initialized = False


def configure_logging():
    global _logger_initialized
    if _logger_initialized:
        return
    _logger_initialized = True

    root = Path(__file__).parent.parent
    logs_dir = root / 'logs'
    logs_dir.mkdir(exist_ok=True)
    log_file = logs_dir / 'app.log'
    log_file.touch(exist_ok=True)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ConsoleFormatter())

    general_logger = logging.getLogger()
    general_logger.setLevel(logging.INFO if not Config.DEBUG else logging.DEBUG)
    general_logger.addHandler(console_handler)

    app_logger = logging.getLogger('app_logger')
    app_handler = RotatingFileHandler(
        filename=root / 'logs' / 'app.log',
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding='utf-8'
    )
    app_handler.setFormatter(ConsoleFormatter())
    app_logger.addHandler(app_handler)
