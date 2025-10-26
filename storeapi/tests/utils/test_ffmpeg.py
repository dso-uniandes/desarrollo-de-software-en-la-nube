from utils import ffmpeg as ffm, ffmpeg


def test_edit_video_function_exists():
    assert callable(ffm.edit_video)
    assert callable(ffmpeg.edit_video)


def test_edit_video_returns_string(monkeypatch, tmp_path):
    class DummyStream:
        def filter(self, *a, **k):
            return self

        def output(self, *a, **k):
            return DummyOutput()

    class DummyOutput:
        def overwrite_output(self):
            return self

        def run(self):
            return 0

    # Mocks críticos
    monkeypatch.setattr(ffm.ffmpeg, "probe", lambda *_a, **_k: {"format": {"duration": "5"}})
    monkeypatch.setattr(ffm.ffmpeg, "input", lambda *a, **k: DummyStream())
    monkeypatch.setattr(ffm.ffmpeg, "output", lambda *a, **k: DummyOutput())
    monkeypatch.setattr(ffm.config, "PROCESSED_FOLDER", str(tmp_path))
    monkeypatch.setattr(ffm.os.path, "exists", lambda p: True)
    monkeypatch.setattr(ffm.os.path, "getsize", lambda p: 1)

    class FakeVideo:
        user_id = 1
        id = 1

    result = ffm.edit_video(b"bytes", "video.mp4", FakeVideo())
    assert isinstance(result, str)


def test_ffmpeg_has_logger():
    logger = getattr(ffmpeg, "logger", None)
    assert logger is not None
    assert hasattr(logger, "info")
    assert callable(logger.info)
