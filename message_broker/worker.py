from datetime import datetime
import json
import os
import sys
import time
import logging
import asyncio
from utils.ffmpeg import edit_video
from utils.config import config
from utils.cloudwatch.metrics import publish_metrics
from message_broker.client import SQS, sqs
from utils.logging_conf import configure_logging
from utils.storage.s3 import (
    get_object_key_from_url,
    get_shared_url,
    get_object,
    s3_upload_video,
)
from storeapi.database import database, video_table

configure_logging(logging.INFO)
logger = logging.getLogger("worker")
logger.setLevel(logging.INFO)


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

    task_start_time = time.time()
    video_id = message.get("video_id", "unknown")
    task_id = message.get("task_id", "unknown")

    logger.info(f"✅ Processing video: {message}")

    # Initialize duration slots
    db_fetch_duration = None
    s3_download_duration = None
    video_processing_duration = None
    db_update_duration = None
    failure_stage = None

    try:
        # ---------------------------
        # DB FETCH
        # ---------------------------
        db_fetch_start = time.time()
        video = await database.fetch_one(
            video_table.select().where(video_table.c.id == int(video_id))
        )
        db_fetch_duration = time.time() - db_fetch_start

        if not video:
            failure_stage = "DB_FETCH"
            raise Exception(f"Video ID {video_id} not found in DB")

        object_key = get_object_key_from_url(video.original_url)

        # ---------------------------
        # S3 DOWNLOAD
        # ---------------------------
        s3_download_start = time.time()
        file_bytes = get_object(object_key)
        if not file_bytes:
            failure_stage = "S3_DOWNLOAD"
            raise Exception(f"Failed to download from S3 for Key: {object_key}")
        s3_download_duration = time.time() - s3_download_start

        # ---------------------------
        # VIDEO PROCESSING (FFmpeg)
        # ---------------------------
        video_processing_start = time.time()
        output_edited_key = edit_video(file_bytes, object_key, video)
        video_processing_duration = time.time() - video_processing_start

        # ---------------------------
        # S3 UPLOAD FINAL VIDEO
        # ---------------------------
        video_name = object_key.split("/")[-1]
        user_id = getattr(video, "user_id", "unknown")

        
        output_key = f"videos/processed/user_{user_id}/{video_name}"

        s3_upload_video(output_edited_key, output_key)
        os.remove(output_edited_key)

        # ---------------------------
        # DATABASE UPDATE
        # ---------------------------
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

        # ---------------------------
        # SUCCESS PATH
        # ---------------------------
        total_duration = time.time() - task_start_time

        logger.info(f"[video_id={video.id}] Video processing complete: {output_key}")
        logger.info(
            f"[task_id={task_id}] TOTAL TASK TIME: {total_duration:.2f}s "
            f"(DB Fetch: {db_fetch_duration:.2f}s, S3 Download: {s3_download_duration:.2f}s, "
            f"FFmpeg: {video_processing_duration:.2f}s, DB Update: {db_update_duration:.2f}s)"
        )

        publish_metrics(
            task_id=task_id,
            total_duration=total_duration,
            db_fetch_duration=db_fetch_duration,
            s3_download_duration=s3_download_duration,
            video_processing_duration=video_processing_duration,
            db_update_duration=db_update_duration,
            success=True,
            failure_stage=None
        )

    except Exception as e:
        total_duration = time.time() - task_start_time

        logger.error(
            f"[task_id={task_id}] ❌ Error processing video after {total_duration:.2f}s (Stage: {failure_stage}) → {str(e)}",
            exc_info=True,
        )

        publish_metrics(
            task_id=task_id,
            total_duration=total_duration,
            db_fetch_duration=db_fetch_duration,
            s3_download_duration=s3_download_duration,
            video_processing_duration=video_processing_duration,
            db_update_duration=db_update_duration,
            success=False,
            failure_stage=failure_stage or "UNKNOWN"
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