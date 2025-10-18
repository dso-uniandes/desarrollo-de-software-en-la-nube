import pytest
from datetime import datetime
from httpx import AsyncClient
from sqlalchemy import insert

from storeapi.database import database, user_table, video_table, video_vote_table


async def _seed_users_and_votes():
    # Users
    users = [
        {"first_name": "Ana", "last_name": "Bravo", "email": "ana@a.com", "password": "x", "city": "Bogotá", "country": "CO"},
        {"first_name": "Beto", "last_name": "Cuevas", "email": "beto@b.com", "password": "x", "city": "Bogotá", "country": "CO"},
        {"first_name": "Caro", "last_name": "Diaz", "email": "caro@c.com", "password": "x", "city": "Medellín", "country": "CO"},
    ]

    result = await database.execute_many(insert(user_table), users)
    # Fetch created ids
    created_users = await database.fetch_all(user_table.select().where(user_table.c.email.in_([u["email"] for u in users])))

    user_id_map = {u.email: u.id for u in created_users}

    # Videos
    ts = datetime(2024, 1, 1)
    videos = [
        {"user_id": user_id_map["ana@a.com"], "title": "v1", "original_url": "u1", "processed_url": "p1",
         "status": "processed", "uploaded_at": ts, "processed_at": ts},
        {"user_id": user_id_map["beto@b.com"], "title": "v2", "original_url": "u2", "processed_url": "p2",
         "status": "processed", "uploaded_at": ts, "processed_at": ts},
        {"user_id": user_id_map["beto@b.com"], "title": "v3", "original_url": "u3", "processed_url": "p3",
         "status": "processed", "uploaded_at": ts, "processed_at": ts},
        {"user_id": user_id_map["caro@c.com"], "title": "v4", "original_url": "u4", "processed_url": "p4",
         "status": "processed", "uploaded_at": ts, "processed_at": ts},
    ]
    await database.execute_many(insert(video_table), videos)

    created_videos = await database.fetch_all(video_table.select())
    vid_by_user = {}
    for v in created_videos:
        vid_by_user.setdefault(v.user_id, []).append(v.id)

    # Votes: Beto should rank above Ana, Ana above Caro
    votes = []
    # Ana: 5 votes on her single video
    for _ in range(5):
        votes.append({"video_id": vid_by_user[user_id_map["ana@a.com"]][0]})
    # Beto: 3 votes on first video, 4 on second => 7 total
    for _ in range(3):
        votes.append({"video_id": vid_by_user[user_id_map["beto@b.com"]][0]})
    for _ in range(4):
        votes.append({"video_id": vid_by_user[user_id_map["beto@b.com"]][1]})
    # Caro: 2 votes
    for _ in range(2):
        votes.append({"video_id": vid_by_user[user_id_map["caro@c.com"]][0]})

    await database.execute_many(insert(video_vote_table), votes)


@pytest.mark.anyio
async def test_ranking_ordering(async_client: AsyncClient):
    await _seed_users_and_votes()
    r = await async_client.get("/api/ranking")
    assert r.status_code == 200
    data = r.json()
    # Positions should be 1..n and sorted by votes desc: Beto(7), Ana(5), Caro(2)
    assert [d["position"] for d in data] == [1, 2, 3]
    assert [d["votes"] for d in data] == [7, 5, 2]
    # Usernames are first_name + last_name
    assert data[0]["username"].startswith("Beto ")


@pytest.mark.anyio
async def test_ranking_city_filter(async_client: AsyncClient):
    await _seed_users_and_votes()
    r = await async_client.get("/api/ranking", params={"city": "Bogotá"})
    assert r.status_code == 200
    data = r.json()
    # Only Ana(5) and Beto(7)
    assert [d["votes"] for d in data] == [7, 5]


@pytest.mark.anyio
async def test_ranking_pagination(async_client: AsyncClient):
    await _seed_users_and_votes()
    # First page size 1
    r1 = await async_client.get("/api/ranking", params={"limit": 1})
    assert r1.status_code == 200
    d1 = r1.json()
    assert len(d1) == 1 and d1[0]["votes"] == 7 and d1[0]["position"] == 1
    # Second page
    r2 = await async_client.get("/api/ranking", params={"offset": 1, "limit": 1})
    assert r2.status_code == 200
    d2 = r2.json()
    assert len(d2) == 1 and d2[0]["votes"] == 5 and d2[0]["position"] == 2


@pytest.mark.anyio
async def test_ranking_invalid_params(async_client: AsyncClient):
    r = await async_client.get("/api/ranking", params={"limit": 0})
    assert r.status_code == 400
    r = await async_client.get("/api/ranking", params={"offset": -1})
    assert r.status_code == 400


@pytest.mark.anyio
async def test_ranking_cache_hit(async_client: AsyncClient, mocker):
    # Seed once; first call stores cache
    await _seed_users_and_votes()
    from utils import cache as cache_module

    # First call builds data
    r1 = await async_client.get("/api/ranking", params={"city": "Bogotá", "limit": 2})
    assert r1.status_code == 200
    data1 = r1.json()

    # Monkeypatch cache_get to return the cached value
    mocker.patch.object(cache_module, "cache_get", new=mocker.AsyncMock(return_value=data1))

    r2 = await async_client.get("/api/ranking", params={"city": "Bogotá", "limit": 2})
    assert r2.status_code == 200
    data2 = r2.json()
    assert data2 == data1


