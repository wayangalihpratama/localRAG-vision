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

            # Get modality from DB
            db_doc = db.query(Document).filter(Document.id == file_id).first()
            if not db_doc:
                raise Exception(f"Document {file_id} not found in DB")

            if db_doc.modality == "video":
                # --- Video Pipeline (STORY-007, STORY-008) ---
                from app.services.video_service import get_video_service

                # 2. Segment Video
                segments = get_video_service().segment_video(local_path)

                # 3. Extract Keyframes
                keyframes_dir = os.path.join(temp_dir, "keyframes")
                keyframe_paths = get_video_service().extract_keyframes(
                    local_path, segments, keyframes_dir
                )

                # 4. Visual Analysis (STORY-008)
                visual_descriptions = get_video_service().analyze_keyframes(
                    keyframe_paths
                )

                # 5. Index Video (STORY-009)
                chunks_indexed = get_indexing_service().index_video(
                    s3_key, segments, visual_descriptions
                )

                db_doc.status = DocumentStatus.COMPLETED
                db_doc.metadata_json = {
                    "scenes": len(segments),
                    "segments": segments,
                    "visual_descriptions": visual_descriptions,
                    "modality": "video",
                }
            else:
                # --- Text/PDF Pipeline ---
                # 2. Extract
                markdown_content = get_extraction_service().extract_markdown(
                    local_path
                )

                # 3. Index
                chunks_indexed = get_indexing_service().index_markdown(
                    s3_key, markdown_content
                )

                # 4. Update Status to COMPLETED
                db_doc.status = DocumentStatus.COMPLETED
                db_doc.metadata_json = {
                    "chunks": chunks_indexed,
                    "length": len(markdown_content),
                    "modality": "text",
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
