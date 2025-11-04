from utils.storage import s3


def test_get_object_key_from_url_extracts_filename():
    url = "http://localhost:9000/videos/sample.mp4"
    key = s3.get_object_key_from_url(url)
    assert key.endswith("sample.mp4")


def test_get_shared_url_returns_http_link(monkeypatch):
    from utils.storage import s3
    monkeypatch.setattr(s3, "get_shared_url", lambda x: f"http://fake-s3-url/{x}")
    file_path = "video.mp4"
    url = s3.get_shared_url(file_path)
    assert "http" in url


def test_s3_get_object_reads_bytes(monkeypatch):
    from utils.storage import s3
    monkeypatch.setattr(s3, "get_object", lambda x: b"123")
    data = s3.get_object("fake-key")
    assert isinstance(data, (bytes, bytearray))
    assert data == b"123"
