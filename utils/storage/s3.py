import logging
import boto3
from typing import Optional
from utils.config import config

logger = logging.getLogger(__name__)

s3 = boto3.client(
    's3',
    aws_access_key_id=config.S3_ACCESS_KEY_ID,
    aws_secret_access_key=config.S3_SECRET_ACCESS_KEY,
    region_name=config.S3_REGION
)


def s3_upload_video(local_file: str, object_name: str) -> str:
    """Simulate uploading a video to S3 by copying the local file to the
    desired object path. This streams the copy to avoid loading the whole
    file into memory and creates parent directories if necessary.
    Returns a fake URL on success, or an empty string on failure.
    """

    logger.debug("Creating and authorizing S3 AWS (local stub)")
    try:
        s3.upload_file(
            local_file,
            config.S3_BUCKET_NAME,
            object_name,
            ExtraArgs={"ExpectedBucketOwner": config.S3_ACCOUNT_ID}
        )
        url = get_shared_url(object_name)
        logger.info("Uploaded %s to S3 as %s, URL: %s", local_file, object_name, url)
        return url
    except Exception as e:
        logger.exception("Error uploading file to S3: %s", e)
        return ""


def get_object(object_name: str) -> Optional[bytes]:
    """Simulate retrieving an object from S3 by reading the local file.
    Returns the file content as bytes on success, or None on failure.
    """

    logger.debug("Accessing S3 bucket (local stub)")
    try:
        response = s3.get_object(
            Bucket="anb-s3-storage",
            Key=object_name,
            ExpectedBucketOwner=config.S3_ACCOUNT_ID)
        content = response['Body'].read()
        logger.debug("Retrieved object %s from S3", object_name)
        return content
    except Exception as e:
        logger.error("Error retrieving file from S3: %s", e)
        return None


def get_shared_url(object_name: str) -> str:
    """Simulate generating a pre-signed URL for an S3 object.
    Returns a fake pre-signed URL.
    """

    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': 'anb-s3-storage', 'Key': object_name},
        ExpiresIn=3600
    )
    logger.debug("Generated pre-signed URL for %s: %s", object_name, url)
    return url


def get_object_key_from_url(url: str) -> str:
    """Extract the object key (path inside the bucket) from an S3 URL."""
    key = url.split(".amazonaws.com/")[-1]
    return key.split("?")[0]
