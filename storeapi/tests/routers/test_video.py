import os
import contextlib
import pathlib
import tempfile
import pytest

from httpx import AsyncClient


@pytest.fixture
def sample_image(fs) -> pathlib.Path:
    path = (pathlib.Path(__file__).parent / "assets" / "myfile.png").resolve()
    fs.create_file(path)
    return path


@pytest.fixture(autouse=True)
def mock_s3_upload_video(mocker):
    return mocker.patch(
        "storeapi.routers.video.s3_upload_video", return_value="https://fakeurl.com")


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
