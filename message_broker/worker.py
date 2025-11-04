from datetime import datetime
import json
import os
import time
from confluent_kafka import Consumer, KafkaException
import logging
import asyncio
from utils.ffmpeg import edit_video
from utils.config import config
from utils.logging_conf import configure_logging
from utils.storage.s3 import get_object_key_from_url, get_shared_url, get_object, s3_upload_video
from storeapi.database import database, video_table

configure_logging()

logger = logging.getLogger('worker')

bootstrap_servers = config.KAFKA_BOOTSTRAP_SERVERS

group_id = config.KAFKA_GROUP_ID

conf = {
    'bootstrap.servers': bootstrap_servers,
    'group.id': group_id,
    'auto.offset.reset': 'earliest'
}


def get_consumer() -> Consumer:
    try:
        if config.ENV_STATE == 'test':
            return None
        return Consumer(conf)
    except Exception as e:
        logger.error(f"Error creating Kafka consumer: {e}")
        return None


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
    video_id = message.get('video_id', 'unknown')
    task_id = message.get('task_id', 'unknown')

    logger.info(f"Processing video: {message}")

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
            logger.error(f"[task_id={task_id}] Failed to get S3 object for Key: {object_key}")
            return
        s3_download_duration = time.time() - s3_download_start

        # Process video with FFmpeg, save to temp file
        video_processing_start = time.time()
        temp_output_path = "/tmp/output.mp4"
        edit_video(file_bytes, object_key, video)
        video_processing_duration = time.time() - video_processing_start

        # Upload processed video to S3
        output_key = f"videos/processed/{object_key.split('/')[-1]}"
        s3_upload_video(temp_output_path, output_key)
        os.remove(temp_output_path)

        # Update database
        db_update_start = time.time()
        await database.execute(
            video_table.update()
            .where(video_table.c.id == video.id)
            .values(
                processed_url=get_shared_url(output_key),
                status="processed",
                processed_at=datetime.now()
            )
        )
        db_update_duration = time.time() - db_update_start

        # Total task time
        total_duration = time.time() - task_start_time
        logger.info(f"[video_id={video.id}] Video processing complete: {output_key}")
        logger.info(
            f"[task_id={task_id}] TOTAL TASK TIME: {total_duration:.2f}s (DB Fetch: {db_fetch_duration:.2f}s, S3 Download: {s3_download_duration:.2f}s, FFmpeg: {video_processing_duration:.2f}s, DB Update: {db_update_duration:.2f}s)")

    except Exception as e:
        total_duration = time.time() - task_start_time
        logger.error(f"[task_id={task_id}] Error processing video after {total_duration:.2f}s: {e}")


async def consume_messages(topic: str, consumer: Consumer):
    consumer.subscribe([topic])
    try:
        while True:
            msg = consumer.poll(1.0)  # Timeout of 1 second
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            decoded_message = msg.value().decode('utf-8')
            logger.info(f"Received message: {decoded_message}")

            if topic == "video_tasks":
                await process_video_processing(json.loads(decoded_message))

    except Exception as e:
        logger.error(f"Error in consumer loop: {e}")
    finally:
        if consumer:
            consumer.close()


async def wrapper_worker():
    try:
        await database.connect()
        logger.info("Database connection established.")
        consumer = get_consumer()
        await consume_messages("video_tasks", consumer)
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
    finally:
        try:
            logger.info("Disconnecting database.")
            await database.disconnect()
        except Exception as e:
            logger.error(f"Error during database disconnection: {e}")


if __name__ == "__main__":
    asyncio.run(wrapper_worker())
