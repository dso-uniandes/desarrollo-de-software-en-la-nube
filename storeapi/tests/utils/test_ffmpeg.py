import utils.ffmpeg as ffmpeg

def test_edit_video_function_exists():
    assert callable(ffmpeg.edit_video)