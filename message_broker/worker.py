from datetime import datetime
import json
import os
from confluent_kafka import Consumer, KafkaException
import logging

from utils.ffmpeg import edit_video
from utils.logging_conf import configure_logging
from utils.s3.s3_local import get_object_key_from_url, get_shared_url, s3_get_object
from storeapi.database import database, video_table
configure_logging()

logger = logging.getLogger('worker')

bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
group_id = os.getenv("KAFKA_GROUP_ID", "video_tasks_group")

conf = {
    'bootstrap.servers': bootstrap_servers,
    'group.id': group_id,
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)

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
    logger.info(f"Processing video: {message}")
    
    video = await database.fetch_one(
        video_table.select().where(video_table.c.id == int(message['video_id']))
    )
    
    if not video:
        logger.error(f"Video not found in database: {message['video_id']}")
        return
        
    logger.info(f"Fetched video from DB: {video.id}")

    object_key = get_object_key_from_url(video.original_url)

    file_bytes = s3_get_object(object_key)
    if not file_bytes:
        logger.error(f"Failed to get S3 object for Key: {object_key}")
        return

    output_key = edit_video(file_bytes, object_key, video)

    await database.execute(
            video_table.update()
            .where(video_table.c.id == video.id)
            .values(
                processed_url=get_shared_url(output_key),
                status="processed",
                processed_at=datetime.now()
            )
        )
            
    logger.info(f"Video Saving complete: {output_key}")



async def consume_messages(topic: str):
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
        consumer.close()
        
import asyncio

async def wrapperWorker():
    try:
        await database.connect()
        logger.info("Database connection established.")
        await consume_messages("video_tasks")
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
    finally:
        try:
            logger.info("Disconnecting database.")
            await database.disconnect()
        except Exception as e:
            logger.error(f"Error during database disconnection: {e}")

if __name__ == "__main__":
    asyncio.run(wrapperWorker())
