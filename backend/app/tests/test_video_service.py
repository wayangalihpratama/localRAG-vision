import pytest
import os
from unittest.mock import MagicMock, patch
from app.services.video_service import VideoService


def test_segment_video_file_not_found():
    service = VideoService()
    with pytest.raises(FileNotFoundError):
        service.segment_video("non_existent.mp4")


@patch("app.services.video_service.detect")
@patch("os.path.exists")
def test_segment_video_success(mock_exists, mock_detect):
    mock_exists.return_value = True

    # Mock scene list from PySceneDetect
    mock_scene = (MagicMock(), MagicMock())
    mock_scene[0].get_seconds.return_value = 0.0
    mock_scene[1].get_seconds.return_value = 10.5

    mock_detect.return_value = [mock_scene]

    service = VideoService()
    segments = service.segment_video("test.mp4")

    assert len(segments) == 1
    assert segments[0] == (0.0, 10.5)
    mock_detect.assert_called_once()


@patch("cv2.VideoCapture")
@patch("cv2.imwrite")
@patch("os.makedirs")
def test_extract_keyframes_success(mock_makedirs, mock_imwrite, mock_capture):
    mock_cap = MagicMock()
    mock_cap.read.return_value = (True, MagicMock())
    mock_capture.return_value = mock_cap

    service = VideoService()
    segments = [(0.0, 10.5), (10.5, 20.0)]
    paths = service.extract_keyframes("test.mp4", segments, "temp_dir")

    assert len(paths) == 2
    assert "keyframe_0000.jpg" in paths[0]
    assert mock_cap.set.call_count == 2
    mock_cap.release.assert_called_once()


@patch("httpx.post")
@patch("builtins.open", new_callable=MagicMock)
def test_analyze_keyframes_success(mock_open, mock_post):
    mock_open.return_value.__enter__.return_value.read.return_value = (
        b"fake_image_data"
    )

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "response": "A person sitting at a desk."
    }
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    service = VideoService()
    descriptions = service.analyze_keyframes(["frame1.jpg"])

    assert len(descriptions) == 1
    assert descriptions[0] == "A person sitting at a desk."
    mock_post.assert_called_once()
