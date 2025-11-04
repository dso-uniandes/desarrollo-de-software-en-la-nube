import logging
import shutil
from pathlib import Path
from typing import Optional
from utils.config import config

logger = logging.getLogger(__name__)


def s3_upload_video(local_file: str, object_name: str) -> str:
    """Simulate uploading a video to S3 by copying the local file to the
    desired object path. This streams the copy to avoid loading the whole
    file into memory and creates parent directories if necessary.

    Returns a fake URL on success, or an empty string on failure.
    """

    logger.debug("Creating and authorizing S3 AWS (local stub)")
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
        logger.info("Uploaded %s to Local as %s, URL: %s", local_file, object_name, url)
        return url
    except Exception as e:
        logger.exception("Error uploading file to S3: %s", e)
        return ""


def s3_get_object(object_name: str) -> Optional[bytes]:
    """Simulate retrieving an object from S3 by reading the local file.

    Returns the file content as bytes on success, or None on failure.
    """

    logger.debug("Accessing S3 bucket (local stub)")
    try:
        path = Path(object_name)

        if not path.exists():
            logger.error("Object does not exist: %s", object_name)
            return None

        with path.open("rb") as f:
            content = f.read()

        logger.debug("Retrieved object %s from Local", object_name)
        return content
    except Exception as e:
        logger.error("Error retrieving file from S3: %s", e)
        return None
    
def get_shared_url(object_name: str) -> str:
    """Simulate generating a pre-signed URL for an S3 object.

    Returns a fake pre-signed URL.
    """

    url = f"http://{config.APP_HOST}/api/videos/stream/{object_name}"
    logger.debug("Generated pre-signed URL for %s: %s", object_name, url)
    return url

def get_object_key_from_url(url: str) -> str:
    """Extract the object key from a given URL."""
    return url.split(f'{config.APP_HOST}/api/videos/stream/')[-1]