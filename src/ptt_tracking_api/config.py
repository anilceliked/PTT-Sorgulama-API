from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="PTT_")

    api_base_url: str = "https://api.ptt.gov.tr/api"
    api_timeout_seconds: int = 20


@lru_cache
def get_settings() -> Settings:
    return Settings()
