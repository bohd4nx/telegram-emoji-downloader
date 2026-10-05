from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    BOT_TOKEN: str
    RATE_LIMIT_COOLDOWN: int = 5

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "emoji-saver"

    # a full URL overrides the POSTGRES_* parts when set
    DATABASE_URL: str = ""

    @model_validator(mode="after")
    def _build_database_url(self) -> "Config":
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        return self


config = Config()  # type: ignore[call-arg]  # BOT_TOKEN is read from the environment
