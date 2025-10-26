import os
import contextlib
import pathlib
import tempfile
import pytest

from datetime import datetime
from httpx import AsyncClient

from ..conftest import registered_user
from storeapi.database import database, video_table


@pytest.fixture
def sample_image(fs) -> pathlib.Path:
    path = (pathlib.Path(__file__).parent / "assets" / "myfile.png").resolve()
    fs.create_file(path)
    return path


@pytest.fixture(autouse=True)
def mock_upload_video(mocker):
    return mocker.patch(
        "storeapi.routers.video.upload_video", return_value="https://fakeurl.com")


@pytest.fixture(autouse=True)
def aiofiles_mock_open(mocker, fs):
    mock_open = (mocker.patch("aiofiles.open")

                 @ contextlib.asynccontextmanager)

    async def async_file_open(fname: str, mode: str = "r"):
        out_fs_mock = mocker.AsyncMock(name=f"async_file_open:{fname!r}/{mode!r}")
        with open(fname, mode) as fin:
            out_fs_mock.read.side_effect = fin.read
            out_fs_mock.write.side_effect = fin.write
            yield out_fs_mock

    mock_open.side_effect = async_file_open
    return mock_open


@pytest.fixture
def mock_uploaded_video(mocker):
    uploaded_video = mocker.Mock(
        id=654321,
        title="Habilidades de dribleo",
        status="uploaded",
        uploaded_at="2025-03-11T10:15:00Z",
        processed_at=None,
        processed_url=None,
    )

    return uploaded_video


@pytest.fixture
def mock_processed_video(mocker, registered_user):
    processed_video = mocker.Mock(
        id=123456,
        user_id=registered_user["id"],
        title="Mi mejor tiro de 3",
        status="processed",
        uploaded_at="2025-03-10T14:30:00Z",
        processed_at="2025-03-10T14:35:00Z",
        processed_url="https://anb.com/videos/processed/123456.mp4",
    )

    return processed_video


async def call_upload_endpoint(
        async_client: AsyncClient, token: str, sample_image: pathlib.Path
):
    return await async_client.post(
        "/api/videos/upload",
        files={
            "file": ("video.mp4", open(sample_image, "rb"), "video/mp4"),
            "title": (None, "Test Video")
        },
        headers={"Authorization": f"Bearer {token}"},
    )


@pytest.mark.anyio
async def test_upload_video(
        async_client: AsyncClient, logged_in_token: str, sample_image: pathlib.Path
):
    response = await call_upload_endpoint(async_client, logged_in_token, sample_image)
    assert response.status_code == 201
    data = response.json()
    assert "task_id" in data
    assert data["message"] == "Successfully uploaded video.mp4"


@pytest.mark.anyio
async def test_temp_file_removed_after_upload(
        async_client: AsyncClient, logged_in_token: str, sample_image: pathlib.Path, mocker
):
    named_temp_file_spy = mocker.spy(tempfile, "NamedTemporaryFile")
    response = await call_upload_endpoint(async_client, logged_in_token, sample_image)
    assert response.status_code == 201
    created_temp_file = named_temp_file_spy.spy_return
    assert not os.path.exists(created_temp_file.name)


@pytest.mark.anyio
async def test_get_videos_returns_empty_list(async_client: AsyncClient, logged_in_token: str):
    response = await async_client.get(
        "/api/videos",
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data == []


@pytest.mark.anyio
async def test_get_videos_uploaded(async_client: AsyncClient, logged_in_token: str, mock_uploaded_video, mocker):
    mocker.patch("storeapi.routers.video.database.fetch_all", return_value=[mock_uploaded_video])

    response = await async_client.get(
        "/api/videos",
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

    video = data[0]
    assert video["status"] == "uploaded"
    assert video["processed_url"] is None
    assert video["processed_at"] is None


@pytest.mark.anyio
async def test_get_videos_processed(
        async_client: AsyncClient, logged_in_token: str, mock_processed_video, mocker
):
    mocker.patch("storeapi.routers.video.database.fetch_all", return_value=[mock_processed_video])

    response = await async_client.get(
        "/api/videos",
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

    video = data[0]
    assert video["status"] == "processed"
    assert video["processed_url"] == "https://anb.com/videos/processed/123456.mp4"
    assert video["processed_at"] == "2025-03-10T14:35:00Z"


@pytest.mark.anyio
async def test_get_video_detail_success(
        async_client: AsyncClient, logged_in_token: str, mock_processed_video, mocker, registered_user
):
    mocker.patch(
        "storeapi.security.get_user",
        return_value=mocker.Mock(
            id=registered_user["id"],
            first_name="John",
            last_name="Doe",
            email="john@email.com",
            city="Bogotá",
            country="Colombia",
        ),
    )

    mocker.patch("storeapi.routers.video.database.fetch_one", return_value=mock_processed_video)

    response = await async_client.get(
        f"/api/videos/{mock_processed_video.id}",
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Mi mejor tiro de 3"
    assert data["status"] == "processed"
    assert data["processed_url"] == "https://anb.com/videos/processed/123456.mp4"
    assert data["processed_at"] == "2025-03-10T14:35:00Z"
    assert "video_id" in data


@pytest.mark.anyio
async def test_delete_video_success(
        async_client: AsyncClient, logged_in_token: str, registered_user
):
    query = video_table.insert().values(
        user_id=registered_user["id"],
        title="Video to delete",
        original_url="https://fakeurl.com/original.mp4",
        processed_url=None,
        status="uploaded",
        uploaded_at=datetime.now(),
    )
    await database.execute(query)
    mock_uploaded_video = await database.fetch_one(
        video_table.select().where(video_table.c.user_id == registered_user["id"]))

    response = await async_client.delete(
        f"/api/videos/{mock_uploaded_video.id}",
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "El video ha sido eliminado exitosamente."


@pytest.mark.anyio
async def test_delete_video_cannot_delete_processed(
        async_client: AsyncClient, logged_in_token: str, registered_user
):
    query = video_table.insert().values(
        user_id=registered_user["id"],
        title="Processed Video",
        original_url="https://fakeurl.com/original.mp4",
        processed_url="https://anb.com/videos/processed/123456.mp4",
        status="processed",
        uploaded_at=datetime.now(),
        processed_at=datetime.now(),
    )
    await database.execute(query)
    mock_processed_video = await database.fetch_one(
        video_table.select().where(video_table.c.user_id == registered_user["id"]))

    response = await async_client.delete(
        f"/api/videos/{mock_processed_video.id}",
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Cannot delete a published video"


@pytest.mark.anyio
async def test_delete_video_not_found(
        async_client: AsyncClient, logged_in_token: str
):
    response = await async_client.delete(
        "/api/videos/99999",
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Video not found"


@pytest.mark.anyio
async def test_upload_video_invalid_file_type(async_client: AsyncClient, logged_in_token: str):
    # Archivo no mp4
    invalid_file = tempfile.NamedTemporaryFile(suffix=".txt", delete=False)
    invalid_file.write(b"not a video")
    invalid_file.close()

    with open(invalid_file.name, "rb") as f:
        response = await async_client.post(
            "/api/videos/upload",
            files={"file": ("invalid.txt", f, "text/plain")},
            headers={"Authorization": f"Bearer {logged_in_token}"},
        )
    assert response.status_code == 400
    assert "Invalid file" in response.json()["detail"]


@pytest.mark.anyio
async def test_stream_video_not_found(async_client: AsyncClient):
    response = await async_client.get("/api/videos/stream/nonexistent.mp4")
    assert response.status_code == 404
    assert response.json()["detail"] == "Video file not found"
