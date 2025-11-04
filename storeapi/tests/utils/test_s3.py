from utils.storage import s3


def test_get_object_key_from_url_extracts_filename():
    url = "http://localhost:9000/videos/sample.mp4"
    key = s3.get_object_key_from_url(url)
    assert key.endswith("sample.mp4")


def test_get_shared_url_returns_http_link(tmp_path):
    file_path = tmp_path / "video.mp4"
    file_path.write_text("fake-data")
    url = s3.get_shared_url(str(file_path))
    assert "http" in url or "file" in url


def test_s3_get_object_reads_bytes(tmp_path, monkeypatch):
    file_path = tmp_path / "data.bin"
    file_path.write_bytes(b"123")

    data = s3.get_object(str(file_path))
    assert isinstance(data, (bytes, bytearray))
    assert data == b"123"
