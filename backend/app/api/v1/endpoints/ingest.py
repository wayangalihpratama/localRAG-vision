import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.schemas.ingest import IngestResponse
from app.services.storage_service import storage_service
from app.worker import process_document

router = APIRouter()


@router.post(
    "/upload",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=IngestResponse,
)  # noqa: E501
async def upload_document(file: UploadFile = File(...)):
    allowed_types = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument."
        "wordprocessingml.document",
        "text/plain",
    ]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file.content_type} not supported.",
        )

    file_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    s3_key = f"{file_id}{file_extension}"

    try:
        # 1. Storage Service Upload
        storage_service.upload_file(file.file, s3_key)

        # 2. Trigger Background Task
        task = process_document.delay(s3_key)

        return {
            "task_id": task.id,
            "file_id": file_id,
            "filename": file.filename,
            "message": "File uploaded successfully. Processing started.",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}",
        )


@router.get("/files", status_code=status.HTTP_200_OK)
async def list_files():
    """
    Returns a list of unique filenames stored in the knowledge base.
    """
    from app.db import get_db

    db = get_db()
    table_name = "knowledge_base"

    if table_name not in db.table_names():
        return []

    table = db.open_table(table_name)
    # Query for unique metadata.source values
    # In LanceDB, we can use to_pandas() or to_arrow() to process metadata
    df = table.to_pandas()
    if df.empty:
        return []

    # Extract filename from metadata
    if "metadata" in df.columns:
        # Assuming metadata is a dict with 'source' or similar
        files = (
            df["metadata"]
            .apply(lambda x: x.get("file") if isinstance(x, dict) else None)
            .unique()
            .tolist()
        )
        return [f for f in files if f]

    return []
