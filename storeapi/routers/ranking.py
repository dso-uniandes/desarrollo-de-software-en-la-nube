import hashlib
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select

from storeapi.config import config
from storeapi.database import database, user_table, video_table, video_vote_table
from storeapi.libs.cache import cache_get, cache_set
from storeapi.models.ranking import RankingItem


router = APIRouter()


def _cache_key(city: Optional[str], offset: int, limit: int) -> str:
    base = f"ranking:city={city or ''}:offset={offset}:limit={limit}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


@router.get("/api/ranking", response_model=List[RankingItem], status_code=200)
async def get_ranking(
    city: Optional[str] = Query(default=None, description="Filtrar por ciudad"),
    offset: int = Query(default=0),
    limit: int = Query(default=50),
):
    # Validate params
    if limit <= 0 or offset < 0:
        raise HTTPException(status_code=400, detail="Parámetro inválido en la consulta.")

    key = _cache_key(city, offset, limit)
    cached = await cache_get(key)
    if cached is not None:
        return [RankingItem(**item) for item in cached]

    # Count votes from video_vote_table
    votes_count = func.count(video_vote_table.c.id).label("votes")

    stmt = (
        select(
            user_table.c.id.label("user_id"),
            (user_table.c.first_name + " " + user_table.c.last_name).label("username"),
            user_table.c.city,
            votes_count,
        )
        .select_from(
            user_table.join(video_table, video_table.c.user_id == user_table.c.id)
            .join(video_vote_table, video_vote_table.c.video_id == video_table.c.id)
        )
        .group_by(user_table.c.id, user_table.c.first_name, user_table.c.last_name, user_table.c.city)
    )

    if city:
        stmt = stmt.where(user_table.c.city == city)

    stmt = stmt.order_by(func.count(video_vote_table.c.id).desc()).offset(offset).limit(limit)

    rows = await database.fetch_all(stmt)

    ranking: List[RankingItem] = []
    for idx, row in enumerate(rows, start=1 + offset):
        ranking.append(
            RankingItem(
                position=idx,
                username=row.username,
                city=row.city,
                votes=row.votes,
            )
        )

    await cache_set(key, [r.model_dump() for r in ranking], ttl_seconds=config.RANKING_CACHE_TTL)

    return ranking

