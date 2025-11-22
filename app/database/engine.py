from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.shared.config import PostgresConfig

DATABASE_URL = (
    f'postgresql+asyncpg://'
    f'{PostgresConfig.POSTGRES_USER}:'
    f'{PostgresConfig.POSTGRES_PASSWORD}'
    f'@{PostgresConfig.POSTGRES_HOST}/{PostgresConfig.POSTGRES_DB}'
)


def engine():
    return create_async_engine(DATABASE_URL)


AsyncSessionLocal = async_sessionmaker(
    bind=engine(),
    expire_on_commit=False
)
