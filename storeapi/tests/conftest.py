import os
from storeapi.database import create_tables_async

os.environ["ENV_STATE"] = "test"

import pytest
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from storeapi.database import (
    database,
    user_table,
    video_table,
    post_table,
    comment_table,
    video_vote_table,
    vote_table,
)
from storeapi.main import app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
def client() -> Generator:
    yield TestClient(app)


@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator:
    await database.connect()
    await create_tables_async()
    yield
    await database.disconnect()


@pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=client.base_url) as ac:
        yield ac


@pytest.fixture(autouse=True)
async def clean_tables(db) -> AsyncGenerator:
    # Clean dependent tables first to satisfy FKs
    # Order: child tables first, then parent tables
    for table in (video_vote_table, comment_table, vote_table, post_table, video_table, user_table):
        try:
            await database.execute(table.delete())
        except Exception as e:
            pass
    yield


@pytest.fixture()
async def registered_user(async_client: AsyncClient) -> dict:
    user_details = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@email.com",
        "password1": "StrongPass123",
        "password2": "StrongPass123",
        "city": "Bogotá",
        "country": "Colombia"
    }
    await async_client.post("/api/auth/signup", json=user_details)
    query = user_table.select().where(user_table.c.email == user_details["email"])
    user = await database.fetch_one(query)
    user_details["id"] = user.id
    user_details["password"] = user_details["password1"]
    return user_details


@pytest.fixture()
async def logged_in_token(async_client: AsyncClient, registered_user: dict) -> str:
    response = await async_client.post(
        "/api/auth/login",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    return response.json()["access_token"]
