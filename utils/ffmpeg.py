import tempfile
from pathlib import Path
import ffmpeg
import os
from utils.config import config
import logging


logger = logging.getLogger('worker')
    
def edit_video(file_bytes: bytes, object_key: str, video) -> str:
    tmp_dir = Path(tempfile.gettempdir())
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
        output_dir = os.path.join(config.PROCESSED_FOLDER, f"user_{video.user_id}")
        os.makedirs(output_dir, exist_ok=True)

        video_name = object_key.split('/')[-1].split('.')[0]
        output_key = os.path.join(output_dir, f"{video_name}.mp4")
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

        return output_key
    except Exception as e:
        logger.exception(f"Error in video processing pipeline: {str(e)}")
        raise Exception(f"Video processing failed")
    finally:
        try:
            Path(temp_file_path).unlink()
            logger.debug(f"Cleaned up temporary file: {temp_file_path}")
        except Exception:
            logger.exception(f"Failed to remove temporary file: {temp_file_path}")