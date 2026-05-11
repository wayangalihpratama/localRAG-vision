import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_video_upload_success(mock_all_services):
    """
    Test that a video file can be uploaded and correctly tagged as 'video'.
    """
    file_content = b"fake video content"
    file = io.BytesIO(file_content)
    files = {"file": ("test.mp4", file, "video/mp4")}

    response = client.post("/api/v1/ingest/upload", files=files)

    assert response.status_code == 202
    data = response.json()
    assert data["filename"] == "test.mp4"
    assert data["modality"] == "video"
    assert "task_id" in data
