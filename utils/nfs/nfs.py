import logging
import shutil
from pathlib import Path
from typing import Optional
from utils.config import config
import os

logger = logging.getLogger(__name__)


def nfs_upload_video(local_file: str, object_name: str) -> str:
    logger.debug("Uploading video to NFS storage")

    try:
        src = Path(local_file)
        dest = Path(object_name)

        if not src.exists():
            logger.error("Source file does not exist: %s", local_file)
            return ""

        # Ensure destination directory exists
        if dest.parent:
            dest.parent.mkdir(parents=True, exist_ok=True)

        # Stream-copy to avoid high memory usage for large files
        with src.open("rb") as fsrc, dest.open("wb") as fdst:
            shutil.copyfileobj(fsrc, fdst)

        url = get_shared_url(object_name)
        logger.info("Uploaded %s to NFS as %s, URL: %s", local_file, object_name, url)
        return url
    except Exception as e:
        logger.exception("Error uploading file to NFS: %s", e)
        return ""


def get_object(object_name: str) -> Optional[bytes]:
    logger.debug("Accessing NFS storage (local stub)")

    try:
        path = Path(object_name)

        if not path.exists():
            logger.error("Object does not exist: %s", object_name)
            return None

        with path.open("rb") as f:
            content = f.read()

        logger.debug("Retrieved object %s from NFS", object_name)
        return content
    except Exception as e:
        logger.error("Error retrieving file from NFS: %s", e)
        return None


def get_shared_url(object_name: str) -> str:
    url = f"http://{config.APP_HOST}/api/videos/stream/{object_name}"
    logger.debug("Generated shared URL for %s: %s", object_name, url)
    return url


def get_object_key_from_url(url: str) -> str:
    return url.split(f'{config.APP_HOST}/api/videos/stream/')[-1]
