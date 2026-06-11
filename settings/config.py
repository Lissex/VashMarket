# settings/config.py
from pathlib import Path
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from .db import DatabaseConfig  # 👈
from .redis import RedisConfig  # 👈

# Получаем корневую директорию проекта
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    bot_token: SecretStr
    database: DatabaseConfig
    redis: RedisConfig
    # shop_id: int
    # api_key: SecretStr
    # api_id: int
    # secret_key: SecretStr
    # merch_id: SecretStr
    # aasecret: SecretStr
    # aapi_key: SecretStr


config = Settings()