import boto3
import logging
from functools import lru_cache
from botocore.exceptions import ClientError

from storeapi.config import config

logger = logging.getLogger(__name__)

AWS_ACCESS_KEY_ID = config.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = config.AWS_SECRET_ACCESS_KEY
AWS_BUCKET_NAME = config.AWS_BUCKET_NAME
AWS_REGION = config.AWS_REGION


@lru_cache()
def s3_get_bucket():
    s3 = boto3.resource(
        "s3",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    logger.debug(f"Accessing S3 bucket: {AWS_BUCKET_NAME} in region {AWS_REGION}")
    return s3.Bucket(AWS_BUCKET_NAME)


def s3_upload_video(local_file: str, object_name: str) -> str:
    bucket = s3_get_bucket()
    logger.debug("Creating and authorizing S3 AWS")
    try:
        bucket.upload_file(local_file, object_name)
        url = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{object_name}"
        logger.debug(f"Uploaded {local_file} to S3 as {object_name}, URL: {url}")
        return url
    except ClientError as e:
        logger.error(f"Error uploading file to S3: {e}")
        return ""
