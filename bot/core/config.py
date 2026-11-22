import logging

from pydantic import SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import ROOT_PATH

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # env_ignore_empty: an empty `KEY=` line counts as unset. Process env wins over the .env file.
    model_config = SettingsConfigDict(env_file=ROOT_PATH / ".env", env_ignore_empty=True, extra="ignore")

    BOT_TOKEN: SecretStr
    DATABASE_URL: SecretStr
    DEBUG: bool = False


def load_settings() -> Settings:
    try:
        return Settings()  # type: ignore[call-arg]
    except ValidationError as exc:
        for error in exc.errors():
            field = ".".join(map(str, error["loc"])) or "unknown"
            logger.error("Invalid configuration for %s: %s", field, error["msg"])
        raise SystemExit(1) from exc


settings = load_settings()
