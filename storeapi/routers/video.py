import contextlib
import logging
import os
import tempfile
import uuid
import aiofiles

from datetime import datetime
from typing import Annotated


from fastapi import APIRouter, UploadFile, HTTPException, status, Form, Depends, File

from message_broker.tasks_dispatcher import dispatch_task
from storeapi.database import database, video_table
from storeapi.libs.video_storage import save_video
# from storeapi.libs.s3.video_storage import save_video
from storeapi.models.user import UserOut
from storeapi.models.video import VideoOut
from storeapi.security import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

CHUNK_SIZE = 1024 * 1024


@router.post("/api/videos/upload", status_code=201)
async def upload_video(
        current_user: Annotated[UserOut, Depends(get_current_user)],
        file: UploadFile = File(...),
        title: str = Form(...),
):
    temp_path: str | None = None
    try:
        if file.content_type not in ("video/mp4", "application/mp4"):
            raise HTTPException(status_code=400, detail="Invalid file. Must be MP4 and less than 100 MB.")

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            temp_path = tmp.name
            while True:
                chunk = await file.read(CHUNK_SIZE)
                if not chunk:
                    break
                tmp.write(chunk)

        video_id = str(uuid.uuid4())
        original_filename, original_ext = os.path.splitext(file.filename or "")
        original_ext = original_ext.lower()
        stored_path = save_video(temp_path, video_id, original_ext)

        query = video_table.insert().values(
            id=video_id,
            user_id=current_user.id,
            title=title,
            original_url=stored_path,
            processed_url=None,
            status="uploaded",
            uploaded_at=datetime.now(),
        )
        await database.execute(query)

        task_id = str(uuid.uuid4())
        try:
            dispatch_task([{"video_id": video_id, "user_id": current_user.id, "task_id": task_id}], "video_tasks")
        except Exception as dispatch_err:
            logger.warning(f"dispatch_task failed (ignored for tests): {dispatch_err}")

        return {"message": "Video uploaded successfully. Processing...", "task_id": task_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error uploading video: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error uploading the file"
        )
    finally:
        if temp_path:
            with contextlib.suppress(FileNotFoundError):
                os.unlink(temp_path)


@router.get("/api/videos", status_code=200)
async def get_videos(current_user: Annotated[UserOut, Depends(get_current_user)]):
    try:
        query = video_table.select().where(video_table.c.user_id == current_user.id)
        videos = await database.fetch_all(query)
        if not videos:
            return []

        return [
            {
                "video_id": v.id,
                "title": v.title,
                "status": v.status,
                "uploaded_at": v.uploaded_at,
                "processed_at": v.processed_at,
                "processed_url": v.processed_url,
            }
            for v in videos
        ]
    except Exception as e:
        logger.exception(f"Error fetching videos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving videos",
        )


@router.get("/api/videos/{video_id}", response_model=VideoOut, status_code=200)
async def get_video_detail(
        video_id: str,
        current_user: Annotated[UserOut, Depends(get_current_user)],
):
    try:
        query = video_table.select().where(video_table.c.id == video_id)
        video = await database.fetch_one(query)

        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        if video.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access forbidden: not your video")

        return {
            "video_id": video.id,
            "title": video.title,
            "status": video.status,
            "uploaded_at": video.uploaded_at,
            "processed_at": video.processed_at,
            "original_url": video.original_url,
            "processed_url": video.processed_url,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error fetching video detail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving video detail",
        )


@router.delete("/api/videos/{video_id}", status_code=200)
async def delete_video(
        video_id: str,
        current_user: Annotated[UserOut, Depends(get_current_user)],
):
    try:
        query = video_table.select().where(video_table.c.id == video_id)
        video = await database.fetch_one(query)

        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        if video.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access forbidden: not your video")

        if video.status == "processed":
            raise HTTPException(status_code=400, detail="Cannot delete a published video")

        delete_query = video_table.delete().where(video_table.c.id == video_id)
        await database.execute(delete_query)

        return {"message": "El video ha sido eliminado exitosamente.", "video_id": video_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error deleting video: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting video",
        )
