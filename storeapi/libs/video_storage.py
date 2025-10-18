import os
import shutil
import logging

logger = logging.getLogger(__name__)

UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")


def save_video(file_path: str, video_id: str, original_ext: str = "") -> str:
    if not os.path.exists(UPLOADS_DIR):
        os.makedirs(UPLOADS_DIR, exist_ok=True)
        logger.debug(f"Created uploads directory at {UPLOADS_DIR}")

    ext = original_ext or os.path.splitext(file_path)[1] or ""
    new_filename = f"{video_id}{ext}"
    dest_path = os.path.join(UPLOADS_DIR, new_filename)

    try:
        shutil.move(file_path, dest_path)
        logger.debug(f"Moved video {file_path} to {dest_path}")
        return f"uploads/{new_filename}"
    except Exception as e:
        logger.error(f"Error moving video file: {e}")
        return ""
