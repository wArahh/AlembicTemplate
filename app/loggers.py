import html
import logging
import os
import queue
import asyncio

import httpx
from logging.handlers import RotatingFileHandler

from app.app_instance.config import Config, FilePaths

async_log_queue = asyncio.Queue(maxsize=1000)


async def telegram_worker():
    async with httpx.AsyncClient(timeout=3) as client:
        while True:
            chat_id, payload = await async_log_queue.get()
            try:
                await client.post(
                    url=f'https://api.telegram.org/bot{Config.TELEGRAM_LOGGER_BOT_TOKEN}/sendMessage',
                    json={**payload, 'chat_id': chat_id}
                )
            except Exception:
                pass
            finally:
                async_log_queue.task_done()


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

        raw_message = record.getMessage()
        allow_html = getattr(record, 'tg_html', False)
        message = raw_message if allow_html else html.escape(raw_message)

        formatted = (
            f'<b>{emoji} {record.levelname}</b> <code>[{asctime}]</code>\n'
            f'<b>Module:</b> <code>{record.name}</code>\n'
            f'<b>Function:</b> <code>{record.funcName}()</code>\n'
            f'<b>Location:</b> <code>{record.filename}:{record.lineno}</code>\n\n'
            f'{message}'
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


class TelegramLogHandler(logging.Handler):
    def emit(self, record):
        try:
            log_entry = self.format(record)
            payload = {
                'text': log_entry[:4096],
                'parse_mode': 'HTML',
                'disable_web_page_preview': True
            }

            for chat_id in Config.TELEGRAM_LOG_RECEIVERS:
                async_log_queue.put_nowait((chat_id, payload))
        except queue.Full:
            pass


def configure_logging():
    telegram_handler = TelegramLogHandler()
    telegram_handler.setLevel(logging.DEBUG if Config.DEBUG else logging.INFO)
    telegram_handler.setFormatter(TelegramFormatter())

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ConsoleFormatter())

    general_logger = logging.getLogger()
    general_logger.setLevel(logging.DEBUG if Config.DEBUG else logging.INFO)
    general_logger.addHandler(console_handler)

    app_instance_logger = logging.getLogger('app_instance_logger')
    app_instance_handler = RotatingFileHandler(
        filename=os.path.join(FilePaths.BASE_DIR, 'logs', 'app_instance_logger.log'),
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding='utf-8'
    )
    app_instance_handler.setFormatter(ConsoleFormatter())
    app_instance_logger.addHandler(app_instance_handler)
    app_instance_logger.addHandler(telegram_handler)

    core_logger = logging.getLogger('core_logger')
    core_handler = RotatingFileHandler(
        filename=os.path.join(FilePaths.BASE_DIR, 'logs', 'core.log'),
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding='utf-8'
    )
    core_handler.setFormatter(ConsoleFormatter())
    core_logger.addHandler(core_handler)
    core_logger.addHandler(telegram_handler)
