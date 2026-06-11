from pydantic import BaseModel, SecretStr


class RedisConfig(BaseModel):
    host: str = "localhost"
    port: int = 6379
    password: SecretStr = SecretStr("")
    db: int = 0

    @property
    def url(self) -> str:
        if self.password.get_secret_value():
            return f"redis://:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"