import io
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_upload_file_success():
    """
    Test that a valid PDF file can be uploaded and returns a task_id.
    Note: We will mock MinIO in actual implementation or use a test bucket.
    """
    file_content = b"Fake PDF content"
    file = io.BytesIO(file_content)

    response = client.post(
        "/api/v1/ingest/upload",
        files={"file": ("test.pdf", file, "application/pdf")},
    )

    assert response.status_code == 202
    assert "task_id" in response.json()


def test_upload_invalid_type():
    """
    Test that invalid file types are rejected.
    """
    file_content = b"Fake EXE content"
    file = io.BytesIO(file_content)

    response = client.post(
        "/api/v1/ingest/upload",
        files={"file": ("test.exe", file, "application/x-msdownload")},
    )

    assert response.status_code == 400
    assert "detail" in response.json()
