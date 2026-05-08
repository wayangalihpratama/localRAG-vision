import pytest  # noqa
from unittest.mock import patch, MagicMock
from app.worker import process_document


@patch("app.worker.s3_client")
@patch("app.worker.get_converter")
def test_process_document_success(mock_get_converter, mock_s3):
    # Mock S3 download
    mock_s3.download_file = MagicMock()

    # Mock Docling conversion
    mock_converter = MagicMock()
    mock_result = MagicMock()
    mock_result.document.export_to_markdown.return_value = (
        "# Test Content\nThis is a table."
    )
    mock_converter.convert.return_value = mock_result
    mock_get_converter.return_value = mock_converter

    # We'll use a dummy s3_key
    s3_key = "test-doc.pdf"

    # Trigger the task synchronously for testing
    result = process_document(s3_key)

    assert result["status"] == "completed"
    assert result["file"] == s3_key
    assert "extraction_length" in result
    assert result["preview"] == "# Test Content\nThis is a table."

    # Verify mocks were called
    mock_s3.download_file.assert_called_once()
    mock_converter.convert.assert_called_once()


@patch("app.worker.s3_client")
def test_process_document_failure(mock_s3):
    # Mock S3 failure
    mock_s3.download_file.side_effect = Exception("S3 Download Error")

    s3_key = "missing-doc.pdf"
    result = process_document(s3_key)

    assert result["status"] == "failed"
    assert "error" in result
    assert "S3 Download Error" in result["error"]
