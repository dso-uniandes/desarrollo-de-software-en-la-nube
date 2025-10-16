from typing import Optional
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    ENV_STATE: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


class GlobalConfig(BaseConfig):
    DATABASE_URL: Optional[str] = None
    DB_FORCE_ROLL_BACK: bool = False
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_BUCKET_NAME: Optional[str] = None
    AWS_REGION: Optional[str] = None
    REDIS_URL: Optional[str] = None
    RANKING_CACHE_TTL: int = 120


class DevConfig(GlobalConfig):
    model_config = SettingsConfigDict(
        env_prefix="DEV_"
    )


class ProdConfig(GlobalConfig):
    model_config = SettingsConfigDict(
        env_prefix="PROD_"
    )


class TestConfig(GlobalConfig):
    DB_FORCE_ROLL_BACK: bool = True

    model_config = SettingsConfigDict(
        env_prefix="TEST_"
    )


@lru_cache()
def get_config(envi_state: str):
    configs = {
        "dev": DevConfig,
        "prod": ProdConfig,
        "test": TestConfig
    }
    return configs[envi_state]()


config = get_config(BaseConfig().ENV_STATE)
