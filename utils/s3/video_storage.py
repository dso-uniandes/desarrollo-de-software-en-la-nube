import os
import logging
import boto3

from botocore.exceptions import ClientError
from storeapi.config import config

logger = logging.getLogger(__name__)

AWS_ACCESS_KEY_ID = config.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = config.AWS_SECRET_ACCESS_KEY
AWS_BUCKET_NAME = config.AWS_BUCKET_NAME
AWS_REGION = config.AWS_REGION

s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)


def save_video(file_path: str, video_id: str) -> str:
    try:
        ext = os.path.splitext(file_path)[1]
        object_key = f"videos/{video_id}{ext}"

        s3_client.upload_file(file_path, AWS_BUCKET_NAME, object_key)
        logger.debug(f"Uploaded {file_path} to S3 bucket {AWS_BUCKET_NAME} as {object_key}")
        return object_key
    except ClientError as e:
        logger.error(f"Error uploading file to S3: {e}")
        return ""
