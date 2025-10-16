import logging
import tempfile
import uuid
import aiofiles

from datetime import datetime
from typing import Annotated


from fastapi import APIRouter, UploadFile, HTTPException, status, Form, Depends, File

from storeapi.database import database, video_table
from storeapi.libs.s3 import s3_upload_video
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
        content = await file.read()
        if file.content_type not in ["video/mp4", "application/mp4"] or len(content) > 100 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Invalid file. Must be MP4 and less than 100 MB.")
        await file.seek(0)

        with tempfile.NamedTemporaryFile() as temp_file:
            filename = temp_file.name
            logger.info(f"Saving uploaded file temporarily to {filename}")
            async with aiofiles.open(filename, "wb") as f:
                while chunk := await file.read(CHUNK_SIZE):
                    await f.write(chunk)

            final_name = title or file.filename
            logger.debug(f"Uploading {filename} to S3 as {final_name}")
            original_url = s3_upload_video(filename, final_name)

        query = video_table.insert().values(
            user_id=current_user.id,
            title=final_name,
            original_url=original_url,
            processed_url=None,
            status="uploaded",
            uploaded_at=datetime.utcnow()
        )
        await database.execute(query)

        task_id = str(uuid.uuid4())

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
