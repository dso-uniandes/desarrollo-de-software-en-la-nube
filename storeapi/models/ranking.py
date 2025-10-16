from pydantic import BaseModel
from typing import Optional


class RankingItem(BaseModel):
    position: int
    username: str
    city: Optional[str]
    likes: int


