import logging
import os
import tempfile
import uuid
import aiofiles

from datetime import datetime
from typing import Annotated


from fastapi import APIRouter, UploadFile, HTTPException, status, Form, Depends, File
from fastapi.responses import StreamingResponse

from message_broker.tasks_dispatcher import dispatch_task
from storeapi.database import database, video_table
from utils.s3.s3_local import s3_upload_video
from utils.config import config
from storeapi.models.user import UserOut
from storeapi.models.video import VideoOut
from storeapi.security import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

CHUNK_SIZE = 1024 * 1024


@router.post("/api/videos/upload", status_code=201)
async def upload_video(current_user: Annotated[UserOut, Depends(get_current_user)],
                       file: UploadFile = File(...),
                       title: str = Form(None),
                       ):
    try:
        ct = (file.content_type or "").lower()
        filename = file.filename or f"{uuid.uuid4()}.mp4"
        ext = (filename.split(".")[-1] if "." in filename else "").lower()
        
        allowed_ct = {"video/mp4", "application/mp4", "application/octet-stream"}
        if ct not in allowed_ct or ext != "mp4":
            raise HTTPException(status_code=400, detail="Invalid file. Must be MP4 and less than 100 MB.")
        
        content = await file.read()
        if len(content) > 100 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Invalid file. Must be MP4 and less than 100 MB.")
        
        await file.seek(0)

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            filename = temp_file.name
            logger.info(f"Saving uploaded file temporarily to {filename}")
            async with aiofiles.open(filename, "wb") as f:
                await f.write(content)

            title_file = title or file.filename
            filename_ext = (file.filename.split('.')[-1] if file.filename and '.' in file.filename else 'mp4')
            final_name = os.path.join(config.UPLOADED_FOLDER, f"user_{current_user.id}", f"{uuid.uuid4()}.{filename_ext}")
            logger.debug(f"Uploading {filename} to S3 as {final_name}")
            original_url = s3_upload_video(filename, final_name)
        
        try:
            os.remove(filename)
        except Exception:
            logger.warning(f"No se pudo borrar temporal {filename}")

        query = video_table.insert().values(
            user_id=current_user.id,
            title=title_file,
            original_url=original_url,
            processed_url=None,
            status="uploaded",
            uploaded_at=datetime.now()
        ).returning(video_table.c.id)
        
        video_id = await database.execute(query)
        task_id = str(uuid.uuid4())
        task_info = {"video_id": video_id, "user_id": current_user.id, "task_id": task_id}
        dispatch_task([task_info], "video_tasks")

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error uploading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="There was an error uploading the file",
        )
    return {"message": f"Successfully uploaded {file.filename}", "task_id": task_id}


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
        video_id: int,
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
        video_id: int,
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

@router.get("/api/videos/stream/{file_path:path}", status_code=200)
async def stream_video(file_path: str):
    try:
        logger.info(f"Streaming video from path: {file_path}")
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Video file not found")

        def file_iterator(path, chunk_size=CHUNK_SIZE):
            with open(path, "rb") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk

        return StreamingResponse(file_iterator(file_path), media_type="video/mp4")

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error streaming video: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error streaming video",
        )

