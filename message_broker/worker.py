import json
import os
from confluent_kafka import Consumer, KafkaException
import logging

import ffmpeg
from utils.logging_conf import configure_logging
from utils.s3.s3_local import s3_get_object
from utils.config import config
from storeapi.database import database, video_table
configure_logging()

logger = logging.getLogger('worker')

bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
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
    logger.info(f"Fetched video from DB: {video.id}")
    
    object_key = video.original_url.split('.com/')[-1]
    
    file_bytes = s3_get_object(object_key)
    if not file_bytes:
        logger.error(f"Failed to get S3 object for Key: {object_key}")
        return

    import tempfile
    from pathlib import Path

    tmp_dir = Path('/tmp')
    tmp_dir.mkdir(parents=True, exist_ok=True)

    file_extension = object_key.split('.')[-1]
    with tempfile.NamedTemporaryFile(
        dir=str(tmp_dir), 
        delete=False, 
        suffix=f'.{file_extension}'
    ) as tf:
        tf.write(file_bytes)
        temp_file_path = tf.name

    try:
        output_dir = Path(os.path.abspath(config.PROCESSED_FOLDER)) / f"user_{video.user_id}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        video_name = object_key.split('/')[-1].split('.')[0]
        output_key = str(output_dir / f"{video_name}.mp4")
        logger.info(f"Output will be saved to: {output_key}")
        
        probe = ffmpeg.probe(temp_file_path)
        duration = float(probe['format']['duration'])
        trim_duration = min(30.0, duration)

        
        intro_path = os.path.join(str(tmp_dir), "intro.mp4")
        main_path = os.path.join(str(tmp_dir), "main.mp4")
        outro_path = os.path.join(str(tmp_dir), "outro.mp4")
        concat_list = os.path.join(str(tmp_dir), "concat_list.txt")
        
        logo_path = os.path.join(os.path.curdir, 'img', 'logo_nba.png')
        logger.info(f"Using logo: {logo_path}")
        
        VIDEO_SETTINGS = {
            'vcodec': 'libx264',
            'acodec': 'aac',
            'ar': '44100',
            'ac': 2,
            'pix_fmt': 'yuv420p',
            'r': 30,
        }
        
        AUDIO_BITRATE = {'b:a': '128k'}
        SEGMENT_DURATION = 2.5
        
        logger.info("Creating intro segment...")
        
        intro_video = ffmpeg.input(logo_path, loop=1, t=SEGMENT_DURATION)
        intro_audio = ffmpeg.input(
            'anullsrc=channel_layout=stereo:sample_rate=44100',
            f='lavfi',
            t=SEGMENT_DURATION
        )
        
        (
            ffmpeg.output(
                intro_video.filter('scale', 1280, 720),
                intro_audio,
                intro_path,
                **VIDEO_SETTINGS,
                **AUDIO_BITRATE
            )
            .overwrite_output()
            .run()
        )
        
        logger.info(f"Processing main video ({trim_duration}s)...")
        
        (
            ffmpeg.input(temp_file_path, t=trim_duration)
            .filter('scale', 1280, 720, force_original_aspect_ratio='decrease')
            .filter('pad', 1280, 720, '(ow-iw)/2', '(oh-ih)/2')
            .output(
                main_path,
                **VIDEO_SETTINGS,
                **AUDIO_BITRATE
            )
            .overwrite_output()
            .run()
        )
        
        logger.info("Creating outro segment...")
        
        outro_video = ffmpeg.input(logo_path, loop=1, t=SEGMENT_DURATION)
        outro_audio = ffmpeg.input(
            'anullsrc=channel_layout=stereo:sample_rate=44100',
            f='lavfi',
            t=SEGMENT_DURATION
        )
        
        (
            ffmpeg.output(
                outro_video.filter('scale', 1280, 720),
                outro_audio,
                outro_path,
                **VIDEO_SETTINGS,
                **AUDIO_BITRATE
            )
            .overwrite_output()
            .run()
        )
        
        logger.info("Creating concatenation manifest...")
        with open(concat_list, "w") as f:
            f.write(f"file '{intro_path}'\n")
            f.write(f"file '{main_path}'\n")
            f.write(f"file '{outro_path}'\n")
        
        logger.info("Concatenating all segments into final video...")
        
        os.makedirs(os.path.dirname(output_key), exist_ok=True)
        
        (
            ffmpeg.input(concat_list, format='concat', safe=0)
            .output(
                output_key,
                vcodec='libx264',
                acodec='aac',
                preset='medium',
                **{'b:v': '2M', 'b:a': '128k'},
                g=30,
                bf=2,
                pix_fmt='yuv420p',
                movflags='faststart',
                r=30
            )
            .overwrite_output()
            .run()
        )
        
        if os.path.exists(output_key) and os.path.getsize(output_key) > 0:
            file_size_mb = os.path.getsize(output_key) / (1024 * 1024)
            logger.info(f"Video processed successfully! Size: {file_size_mb:.2f} MB")
        else:
            logger.error(f"Output file missing or empty: {output_key}")
            raise FileNotFoundError(f"Output file not found or empty: {output_key}")
    
        await database.execute(
            video_table.update()
            .where(video_table.c.id == video.id)
            .values(
                processed_url=f"http://fake_s3.com/{output_key}",
                status="processed"
            )
        )
            
        logger.info(f"Video processing complete: {output_key}")
        
    except Exception as e:
        logger.exception(f"Error processing video: {e}")
    finally:
        try:
            Path(temp_file_path).unlink()
            logger.debug(f"Cleaned up temporary file: {temp_file_path}")
        except Exception:
            logger.exception(f"Failed to remove temporary file: {temp_file_path}")



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