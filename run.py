import asyncio
import subprocess

from app.main import supercalifragilisticexpialidocious_func
from app.loggers import configure_logging

async def run_all():
    subprocess.run(['alembic', 'upgrade', 'head'])
    configure_logging()
    await supercalifragilisticexpialidocious_func()


if __name__ == '__main__':
    asyncio.run(run_all())
