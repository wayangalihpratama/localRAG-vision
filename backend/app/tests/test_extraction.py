from unittest.mock import patch, MagicMock
from app.worker import process_document


@patch("app.worker.storage_service")
@patch("app.worker.get_extraction_service")
@patch("app.worker.get_indexing_service")
def test_process_document_success(
    mock_get_indexing, mock_get_extraction, mock_storage
):
    mock_indexing = MagicMock()
    mock_get_indexing.return_value = mock_indexing

    mock_extraction = MagicMock()
    mock_get_extraction.return_value = mock_extraction

    # Mock Storage
    mock_storage.download_file.return_value = "/tmp/test.pdf"

    # Mock Extraction
    mock_extraction.extract_markdown.return_value = "# Test Content"

    # Mock Indexing
    mock_indexing.index_markdown.return_value = 1

    file_id = "test-id"
    s3_key = "test-doc.pdf"

    # Mock SQL DB in worker
    with patch("app.worker.get_session_local") as mock_get_session:
        mock_db_session = MagicMock()
        mock_get_session.return_value = MagicMock(return_value=mock_db_session)

        result = process_document(file_id, s3_key)

    assert result["status"] == "completed"
    assert result["file_id"] == file_id
    assert result["chunks_indexed"] == 1


@patch("app.worker.storage_service")
def test_process_document_failure(mock_storage):
    mock_storage.download_file.side_effect = Exception("Storage Error")

    file_id = "test-id"
    s3_key = "missing.pdf"

    with patch("app.worker.get_session_local") as mock_get_session:
        mock_db_session = MagicMock()
        mock_get_session.return_value = MagicMock(return_value=mock_db_session)

        result = process_document(file_id, s3_key)

    assert result["status"] == "failed"
    assert "Storage Error" in result["error"]
