from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VideoIn(BaseModel):
    title: str


class VideoOut(BaseModel):
    video_id: str
    title: str
    status: str
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    processed_url: Optional[str] = None

    model_config = {"from_attributes": True}


class VideoDB(VideoOut):
    user_id: str
    original_url: str
    processed_url: Optional[str] = None
    status: str
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
