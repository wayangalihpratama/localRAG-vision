import pytest
import sys
from unittest.mock import MagicMock, patch

# --- 1. Global Module Mocks ---
mock_modules = [
    "sentence_transformers",
    "lancedb",
    "boto3",
    "botocore",
    "botocore.client",
    "redis",
    "docling",
    "docling.document_converter",
]
for mod in mock_modules:
    sys.modules[mod] = MagicMock()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    from app.db import Base, get_engine

    # Force engine creation with in-memory URL
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def db_session(setup_test_db):
    from app.db import get_session_local

    TestingSessionLocal = get_session_local()
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def mock_all_services():
    with patch(
        "app.services.storage_service.storage_service"
    ) as mock_storage, patch("app.db.get_db") as mock_vdb, patch(
        "app.db.get_embedding_model"
    ) as mock_embed, patch(
        "app.services.extraction_service.get_extraction_service"
    ), patch(
        "app.services.indexing_service.get_indexing_service"
    ), patch(
        "app.worker.process_document.delay"
    ) as mock_celery, patch(
        "httpx.AsyncClient"
    ) as mock_httpx:

        mock_storage.upload_file.return_value = "test-key"
        mock_vdb.return_value = MagicMock()
        mock_embed.return_value = MagicMock()
        mock_celery.return_value = MagicMock(id="test-task-id")

        # Setup httpx mock defaults
        mock_instance = mock_httpx.return_value
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.get.return_value = MagicMock(
            status_code=200, json=lambda: {}
        )
        mock_instance.post.return_value = MagicMock(
            status_code=200, json=lambda: {}
        )
        mock_instance.delete.return_value = MagicMock(
            status_code=200, json=lambda: {}
        )

        yield
