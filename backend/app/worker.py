import os
import tempfile
from celery import Celery
from app.config import settings
from app.services.storage_service import storage_service
from app.services.extraction_service import get_extraction_service
from app.services.indexing_service import get_indexing_service
from app.db import get_session_local
from app.models.document import Document, DocumentStatus

celery_app = Celery(
    "worker", broker=settings.REDIS_URL, backend=settings.REDIS_URL
)


@celery_app.task(name="process_document")
def process_document(file_id: str, s3_key: str):
    """
    Orchestrates the document processing pipeline and updates the SQL DB.
    """
    db = get_session_local()()
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            local_path = os.path.join(temp_dir, s3_key)

            # 1. Download
            storage_service.download_file(s3_key, local_path)

            # 2. Extract
            markdown_content = get_extraction_service().extract_markdown(
                local_path
            )

            # 3. Index
            chunks_indexed = get_indexing_service().index_markdown(
                s3_key, markdown_content
            )

            # 4. Update Status to COMPLETED
            db_doc = db.query(Document).filter(Document.id == file_id).first()
            if db_doc:
                db_doc.status = DocumentStatus.COMPLETED
                db_doc.metadata_json = {
                    "chunks": chunks_indexed,
                    "length": len(markdown_content),
                }
                db.commit()

            return {
                "status": "completed",
                "file_id": file_id,
                "chunks_indexed": chunks_indexed,
            }

    except Exception as e:
        # Update Status to FAILED
        db_doc = db.query(Document).filter(Document.id == file_id).first()
        if db_doc:
            db_doc.status = DocumentStatus.FAILED
            db_doc.metadata_json = {"error": str(e)}
            db.commit()
        return {"status": "failed", "file_id": file_id, "error": str(e)}
    finally:
        db.close()
