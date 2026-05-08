import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_upload_file_success(mock_all_services):
    """
    Test that a valid file can be uploaded.
    External services are mocked in conftest.py.
    """
    file_content = b"Fake PDF content"
    file = io.BytesIO(file_content)
    response = client.post(
        "/api/v1/ingest/upload",
        files={"file": ("test.pdf", file, "application/pdf")},
    )
    assert response.status_code == 202
    assert "task_id" in response.json()
    assert "file_id" in response.json()


def test_list_files(mock_all_services):
    """
    Test that the /files endpoint returns a list.
    """
    response = client.get("/api/v1/ingest/files")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_delete_file_success(mock_all_services):
    """
    Test that a document can be deleted.
    """
    # 1. Upload
    file_content = b"Content to delete"
    file = io.BytesIO(file_content)
    upload_res = client.post(
        "/api/v1/ingest/upload",
        files={"file": ("delete_me.txt", file, "text/plain")},
    )
    file_id = upload_res.json()["file_id"]

    # 2. Delete
    delete_res = client.delete(f"/api/v1/ingest/files/{file_id}")
    assert delete_res.status_code == 204

    # 3. Verify
    list_res = client.get("/api/v1/ingest/files")
    assert not any(f["id"] == file_id for f in list_res.json())
