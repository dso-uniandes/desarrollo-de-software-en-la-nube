from datetime import datetime
import json
import os
import sys
import time
import logging
import asyncio
from utils.ffmpeg import edit_video
from utils.config import config
from message_broker.client import SQS, sqs
from utils.logging_conf import configure_logging
from utils.storage.s3 import (
    get_object_key_from_url,
    get_shared_url,
    get_object,
    s3_upload_video,
)
from storeapi.database import database, video_table

configure_logging()

logger = logging.getLogger("worker")


async def process_video_processing(message: dict):
    """
    Process a video by adding intro/outro branding and trimming to 30 seconds max.

    This function performs the following steps:
    1. Retrieves video metadata from database
    2. Downloads the original video from S3
    3. Creates branded intro and outro segments with logo
    4. Trims and processes the main video content
    5. Concatenates all segments into a final video
    6. Updates the database with the processed video URL

    Args:
        message: Dictionary containing 'video_id' of the video to process

    The final video structure is: [Intro (2.5s)] + [Main Video (max 30s)] + [Outro (2.5s)]
    All segments are standardized to 1280x720 @ 30fps with AAC audio.
    """
    # Start timing the task
    task_start_time = time.time()
    video_id = message.get("video_id", "unknown")
    task_id = message.get("task_id", "unknown")

    logger.info(f"✅ Processing video: {message}")

    try:
        # Fetch video from database
        db_fetch_start = time.time()
        video = await database.fetch_one(
            video_table.select().where(video_table.c.id == int(video_id))
        )
        db_fetch_duration = time.time() - db_fetch_start

        if not video:
            logger.error(f"Video ID {video_id} not found in DB")
            return

        object_key = get_object_key_from_url(video.original_url)

        # Download from S3
        s3_download_start = time.time()
        file_bytes = get_object(object_key)
        if not file_bytes:
            logger.error(
                f"[task_id={task_id}] Failed to get S3 object for Key: {object_key}"
            )
            return
        s3_download_duration = time.time() - s3_download_start

        # Process video with FFmpeg, save to temp file
        video_processing_start = time.time()
        edit_video(file_bytes, object_key, video)
        video_processing_duration = time.time() - video_processing_start

        # Upload processed video to S3
        video_name = object_key.split("/")[-1]
        user_id = video.user_id if hasattr(video, "user_id") else "unknown"

        final_video_path = f"videos/processed/user_{user_id}/{video_name}"
        output_key = f"videos/processed/user_{user_id}/{video_name}"

        s3_upload_video(final_video_path, output_key)
        os.remove(final_video_path)

        # Update database
        db_update_start = time.time()
        await database.execute(
            video_table.update()
            .where(video_table.c.id == video.id)
            .values(
                processed_url=get_shared_url(output_key),
                status="processed",
                processed_at=datetime.now(),
            )
        )
        db_update_duration = time.time() - db_update_start

        # Total task time
        total_duration = time.time() - task_start_time
        logger.info(f"[video_id={video.id}] Video processing complete: {output_key}")
        logger.info(
            f"[task_id={task_id}] TOTAL TASK TIME: {total_duration:.2f}s (DB Fetch: {db_fetch_duration:.2f}s, S3 Download: {s3_download_duration:.2f}s, FFmpeg: {video_processing_duration:.2f}s, DB Update: {db_update_duration:.2f}s)"
        )

    except Exception as e:
        total_duration = time.time() - task_start_time
        logger.error(
            f"[task_id={task_id}] Error processing video after {total_duration:.2f}s: {e}"
        )


async def consume_messages(topic: str, consumer: SQS):
    logger.info(f"🎧 Worker listening for SQS messages on topic '{topic}'...")

    try:
        while True:
            response = consumer.receive_message(
                QueueUrl=config.VIDEO_QUEUE_URL,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=5,
                AttributeNames=["All"],
                VisibilityTimeout=120,
            )
            messages = response.get("Messages", [])
            if not messages:
                continue

            for msg in messages:
                body = msg["Body"]
                decoded_message = json.loads(body)
                receipt_handle = msg["ReceiptHandle"]
                logger.info(f"📩 Received message: {body}")
                await process_video_processing(decoded_message)
                consumer.delete_message(
                    QueueUrl=config.VIDEO_QUEUE_URL, ReceiptHandle=receipt_handle
                )
    except Exception as e:
        logger.error(f"Error in consumer loop: {e}")


async def wrapper_worker():
    try:
        await database.connect()
        logger.info("Database connection established.")

        if not sqs:
            logger.error("SQS client not initialized. Check ENV_STATE or SQS config.")
            return
        await consume_messages("video_tasks", sqs)
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
    finally:
        try:
            logger.info("Disconnecting database.")
            await database.disconnect()
        except Exception as e:
            logger.error(f"Error during database disconnection: {e}")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(wrapper_worker())
