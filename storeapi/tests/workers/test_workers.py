import pytest
from unittest.mock import AsyncMock, patch
from message_broker import worker

@pytest.mark.asyncio
async def test_process_video_processing_success(monkeypatch):
    # Simula video en la base de datos
    fake_video = type("Video", (), {
        "id": 1,
        "user_id": 99,
        "original_url": "http://localhost/api/videos/stream/user_99/input.mp4"
    })()

    # Mock de dependencias
    monkeypatch.setattr(worker.database, "fetch_one", AsyncMock(return_value=fake_video))
    monkeypatch.setattr(worker, "get_object_key_from_url", lambda url: "user_99/input.mp4")
    monkeypatch.setattr(worker, "edit_video", lambda b, k, v: "user_99/output.mp4")
    monkeypatch.setattr(worker, "get_shared_url", lambda key: f"http://localhost/api/videos/stream/{key}")
    monkeypatch.setattr(worker.database, "execute", AsyncMock(return_value=None))

    message = {"video_id": 1, "task_id": "abc123"}
    await worker.process_video_processing(message)


@pytest.mark.asyncio
async def test_process_video_processing_fails(monkeypatch):
    # Simula error en descarga
    monkeypatch.setattr(worker.database, "fetch_one", AsyncMock(return_value=None))
    message = {"video_id": 999, "task_id": "err001"}

    # No debe lanzar excepción fatal
    await worker.process_video_processing(message)