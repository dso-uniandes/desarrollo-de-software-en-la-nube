import os
import logging

from typing import Optional
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class BaseConfig(BaseSettings):
    ENV_STATE: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


class GlobalConfig(BaseConfig):
    DATABASE_URL: Optional[str] = None
    DB_FORCE_ROLL_BACK: bool = False

    S3_ACCESS_KEY_ID: Optional[str] = None
    S3_SECRET_ACCESS_KEY: Optional[str] = None
    S3_BUCKET_NAME: Optional[str] = None
    S3_REGION: Optional[str] = None
    S3_ACCOUNT_ID: Optional[str] = None

    REDIS_URL: Optional[str] = None
    RANKING_CACHE_TTL: int = 120
    KAFKA_BOOTSTRAP_SERVERS: Optional[str] = None

    VIDEO_STORAGE_BASE: str = os.getenv("VIDEO_STORAGE_PATH", "videos")
    UPLOADED_FOLDER: str = f"{VIDEO_STORAGE_BASE}/uploaded"
    PROCESSED_FOLDER: str = f"{VIDEO_STORAGE_BASE}/processed"
    KAFKA_GROUP_ID: str = 'video_tasks_group'
    APP_HOST: Optional[str] = None


class DevConfig(GlobalConfig):
    S3_ACCOUNT_ID: Optional[str] = None
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
    config_instance = configs[envi_state]()
    config_instance.ENV_STATE = envi_state
    return config_instance


config = get_config(BaseConfig().ENV_STATE)

if config.ENV_STATE == "test":
    config.VIDEO_STORAGE_BASE = "./videos"
    config.UPLOADED_FOLDER = f"{config.VIDEO_STORAGE_BASE}/uploaded"
    config.PROCESSED_FOLDER = f"{config.VIDEO_STORAGE_BASE}/processed"

for dir in [config.PROCESSED_FOLDER, config.UPLOADED_FOLDER]:
    os.makedirs(dir, exist_ok=True)


def get_storage_base_path():
    return os.getenv("VIDEO_STORAGE_PATH", os.path.join(os.getcwd(), "videos"))
