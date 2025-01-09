import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from dotenv import load_dotenv

load_dotenv()

POSTGRES_DB: str = os.getenv('POSTGRES_DB', '')
POSTGRES_HOST: str = os.getenv('POSTGRES_HOST', '')
POSTGRES_USER: str = os.getenv('POSTGRES_USER', '')
POSTGRES_PASSWORD: str = os.getenv('POSTGRES_PASSWORD', '')

DATABASE_URL = (
    f'postgresql+asyncpg://'
    f'{POSTGRES_USER}:'
    f'{POSTGRES_PASSWORD}'
    f'@{POSTGRES_HOST}/{POSTGRES_DB}'
)

sessionmaker = async_sessionmaker(
    create_async_engine(DATABASE_URL), expire_on_commit=False
)
