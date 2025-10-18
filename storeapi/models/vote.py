from pydantic import BaseModel
from datetime import datetime


class VoteIn(BaseModel):
    video_id: str
    vote_type: str  # "like" o "dislike"


class Vote(BaseModel):
    id: str
    user_id: str
    video_id: str
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
