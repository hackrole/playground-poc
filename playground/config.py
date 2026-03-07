import logging
from functools import lru_cache
from typing import Any, Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from playground.constants import (
    DEFAULT_SIGNED_URL_EXPIRY,
    S3_BUCKET_NAME,
    TOKEN_BUCKET_CAPACITY,
    TOKEN_BUCKET_REFILL_RATE,
    AppEnv,
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PLAYGROUND_",
        env_file_encoding="utf-8",
    )

    app_env: AppEnv = AppEnv.DEVELOPMENT
    log_level: str | int = logging.INFO

    token_bucket_capacity: int = TOKEN_BUCKET_CAPACITY
    token_bucket_refill_rate: int = TOKEN_BUCKET_REFILL_RATE

    s3_endpoint_url: Optional[str] = None
    s3_access_key: Optional[str] = None
    s3_secret_key: Optional[str] = None
    s3_region_name: str = "us-east-1"
    s3_bucket_name: str = S3_BUCKET_NAME
    signed_url_expiry: int = DEFAULT_SIGNED_URL_EXPIRY

    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None


@lru_cache
def get_settings() -> Settings:
    return Settings()


class Config:
    _instance: Optional["Settings"] = None

    def setup(self) -> None:
        if self._instance is None:
            self._instance = get_settings()

    def __getattr__(self, name: str) -> Any:
        if self._instance is None:
            raise RuntimeError(
                "Config not initialized. Call config.setup() in create_app() before accessing settings."
            )
        return getattr(self._instance, name)

    def __repr__(self) -> str:
        if self._instance is None:
            return "<Config: not initialized>"
        return f"<Config: {self._instance}>"


config = Config()
