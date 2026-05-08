import pytest
from unittest.mock import patch, MagicMock
from app.worker import process_document


@patch("app.worker.storage_service")
@patch("app.worker.extraction_service")
@patch("app.worker.indexing_service")
def test_process_document_success(
    mock_indexing, mock_extraction, mock_storage
):
    # Mock Storage
    mock_storage.download_file.return_value = "/tmp/test.pdf"

    # Mock Extraction
    mock_extraction.extract_markdown.return_value = "# Test Content"

    # Mock Indexing
    mock_indexing.index_markdown.return_value = 1

    s3_key = "test-doc.pdf"
    result = process_document(s3_key)

    assert result["status"] == "completed"
    assert result["file"] == s3_key
    assert result["chunks_indexed"] == 1

    # Verify service calls
    mock_storage.download_file.assert_called_once()
    mock_extraction.extract_markdown.assert_called_once()
    mock_indexing.index_markdown.assert_called_once()


@patch("app.worker.storage_service")
def test_process_document_failure(mock_storage):
    # Mock failure
    mock_storage.download_file.side_effect = Exception("Storage Error")

    s3_key = "missing.pdf"
    result = process_document(s3_key)

    assert result["status"] == "failed"
    assert "Storage Error" in result["error"]
