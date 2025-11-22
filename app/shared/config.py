import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    DEBUG = os.getenv('DEBUG')


class PostgresConfig(Config):
    POSTGRES_DB: str = os.getenv('POSTGRES_DB')
    POSTGRES_HOST: str = os.getenv('POSTGRES_HOST')
    POSTGRES_USER: str = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD: str = os.getenv('POSTGRES_PASSWORD')
