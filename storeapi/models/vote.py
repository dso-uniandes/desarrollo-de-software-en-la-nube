from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class VoteIn(BaseModel):
    vote_type: str  # "like" o "dislike"


class Vote(BaseModel):
    id: int
    user_id: int
    video_id: int
    vote_type: str
    created_at: datetime

    model_config = {"from_attributes": True}


class VideoWithVotes(BaseModel):
    video: "VideoOut"
    likes: int
    dislikes: int
    user_vote: str | None = None

from storeapi.models.video import VideoOut
VideoWithVotes.model_rebuild()
