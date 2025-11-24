import os

os.environ["ENV_STATE"] = "test"

from storeapi.database import create_tables_async

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
)
from storeapi.main import app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
def client() -> Generator:
    yield TestClient(app)


@pytest.fixture(scope="session", autouse=True)
async def create_test_database():
    await create_tables_async()
    yield


@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator:
    await database.connect()
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
    for table in (video_vote_table, comment_table, post_table, video_table, user_table):
        await database.execute(table.delete())
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


@pytest.fixture(autouse=True)
def mock_upload_video(mocker):
    return mocker.patch("storeapi.routers.video.upload_video", return_value="https://fakeurl.com")


@pytest.fixture(autouse=True)
def mock_dispatch_task(mocker):
    return mocker.patch("storeapi.routers.video.dispatch_task", return_value=None)


@pytest.fixture()
def presigned_fake_user(mocker, registered_user):
    user = mocker.Mock()
    user.id = registered_user["id"]
    user.email = registered_user["email"]
    user.first_name = "Fake"
    user.last_name = "User"
    user.token = "fake.jwt.token"
    return user


@pytest.fixture()
def presigned_fake_video(mocker, registered_user):
    video = mocker.Mock()
    video.id = 999
    video.user_id = registered_user["id"]
    video.title = "Test Video"
    video.original_url = f"videos/uploaded/user_{registered_user['id']}/fake.mp4"
    return video
