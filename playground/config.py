from functools import lru_cache
from typing import Optional

from pydantic import ConfigDict
from pydantic_settings import BaseSettings

from playground.constants import (
    DEFAULT_CONCURRENT,
    DEFAULT_SIGNED_URL_EXPIRY,
    S3_BUCKET_NAME,
    TOKEN_BUCKET_CAPACITY,
    TOKEN_BUCKET_REFILL_RATE,
    AppEnv,
)


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_prefix="PLAYGROUND_",
        case_sensitive=False,
    )

    app_env: AppEnv = AppEnv.DEVELOPMENT
    s3_endpoint_url: Optional[str] = None
    s3_access_key: Optional[str] = None
    s3_secret_key: Optional[str] = None
    s3_region_name: str = "us-east-1"
    s3_bucket_name: str = S3_BUCKET_NAME
    signed_url_expiry: int = DEFAULT_SIGNED_URL_EXPIRY
    default_concurrent: int = DEFAULT_CONCURRENT
    token_bucket_capacity: int = TOKEN_BUCKET_CAPACITY
    token_bucket_refill_rate: int = TOKEN_BUCKET_REFILL_RATE


@lru_cache
def get_settings() -> Settings:
    return Settings()
