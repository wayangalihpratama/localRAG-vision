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
