from pydantic import BaseModel, SecretStr
from sqlalchemy import URL
from typing import Optional
from urllib.parse import quote_plus


class DatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = 5432
    user: str = "loop_admin"
    password: SecretStr
    name: str = "loop_db"
    driver: str = "postgresql+asyncpg"

    # Опционально: SSL режим
    ssl_mode: Optional[str] = None

    @property
    def db_url(self) -> URL:
        """Создает URL для SQLAlchemy"""
        return URL.create(
            drivername=self.driver,
            username=self.user,
            password=self.password.get_secret_value(),
            host=self.host,
            port=self.port,
            database=self.name,
        )

    @property
    def dsn(self) -> str:
        """Собираем DSN вручную, чтобы избежать багов URL.create()"""
        pwd = quote_plus(self.password.get_secret_value())
        return f"{self.driver}://{self.user}:{pwd}@{self.host}:{self.port}/{self.name}"

    class Config:
        # Позволяет использовать SecretStr правильно
        arbitrary_types_allowed = True