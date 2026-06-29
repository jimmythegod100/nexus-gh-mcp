from functools import lru_cache
import logging

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    SERVICE_NAME: str = "nexus-gh-mcp"
    SERVICE_PORT: int = 8003
    LOG_LEVEL: str = "INFO"
    GITHUB_TOKEN: str = "test-token"
    GITHUB_OWNER: str = "jimmythegod100"
    GITHUB_API_URL: str = "https://api.github.com"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def setup_logging() -> None:
    settings = get_settings()
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
