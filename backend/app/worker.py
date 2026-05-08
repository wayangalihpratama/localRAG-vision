import os
import tempfile
from celery import Celery
from app.config import settings
from app.services.storage_service import storage_service
from app.services.extraction_service import extraction_service
from app.services.indexing_service import indexing_service

celery_app = Celery(
    "worker", broker=settings.REDIS_URL, backend=settings.REDIS_URL
)


@celery_app.task(name="process_document")
def process_document(s3_key: str):
    """
    Orchestrates the document processing pipeline using specialized services.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        local_path = os.path.join(temp_dir, s3_key)

        try:
            # 1. Download
            storage_service.download_file(s3_key, local_path)

            # 2. Extract
            markdown_content = extraction_service.extract_markdown(local_path)

            # 3. Index
            chunks_indexed = indexing_service.index_markdown(
                s3_key, markdown_content
            )

            return {
                "status": "completed",
                "file": s3_key,
                "chunks_indexed": chunks_indexed,
                "extraction_length": len(markdown_content),
            }

        except Exception as e:
            return {"status": "failed", "file": s3_key, "error": str(e)}
