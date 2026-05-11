import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.db import get_sql_db
from app.services.storage_service import storage_service
from app.models.document import Document, DocumentStatus
from app.schemas.ingest import IngestResponse
from app.worker import process_document

router = APIRouter()


@router.post(
    "/upload",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=IngestResponse,
)  # noqa: E501
async def upload_document(
    file: UploadFile = File(...), db: Session = Depends(get_sql_db)
):
    allowed_types = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument."
        "wordprocessingml.document",
        "text/plain",
        "video/mp4",
        "video/quicktime",
    ]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file.content_type} not supported.",
        )

    file_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    s3_key = f"{file_id}{file_extension}"

    # 1. Storage Service Upload
    storage_service.upload_file(file.file, s3_key)

    # 2. Create DB Record
    modality = "video" if file.content_type.startswith("video/") else "text"
    db_doc = Document(
        id=file_id,
        filename=file.filename,
        s3_key=s3_key,
        status=DocumentStatus.PROCESSING,
        modality=modality,
    )
    db.add(db_doc)
    db.commit()

    # 3. Trigger Background Task
    task = process_document.delay(file_id, s3_key)

    # 4. Update task_id in DB
    db_doc.task_id = task.id
    db.commit()

    return {
        "task_id": task.id,
        "file_id": file_id,
        "filename": file.filename,
        "modality": modality,
        "message": "File uploaded successfully. Processing started.",
    }


@router.get("/files", status_code=status.HTTP_200_OK)
async def list_files(db: Session = Depends(get_sql_db)):
    """
    Returns a list of documents and their statuses from the tracking DB.
    """
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "status": doc.status,
            "modality": doc.modality,
            "created_at": doc.created_at,
        }
        for doc in docs
    ]


@router.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(file_id: str, db: Session = Depends(get_sql_db)):
    """
    Deletes a document from SQL DB, MinIO storage, and LanceDB vector store.
    """
    doc = db.query(Document).filter(Document.id == file_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    try:
        # 1. Delete from MinIO
        storage_service.delete_file(doc.s3_key)

        # 2. Delete from LanceDB
        from app.db import get_db

        vdb = get_db()
        table_name = "knowledge_base"
        if table_name in vdb.table_names():
            table = vdb.open_table(table_name)
            # Delete where metadata.file == s3_key
            table.delete(f'metadata.file = "{doc.s3_key}"')

        # 3. Delete from SQL DB
        db.delete(doc)
        db.commit()

        return None
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Deletion failed: {str(e)}",
        )


@router.get("/status/{task_id}", status_code=status.HTTP_200_OK)
async def get_task_status(task_id: str, db: Session = Depends(get_sql_db)):
    """
    Returns the status of a document processing task.
    """
    doc = db.query(Document).filter(Document.task_id == task_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return {
        "task_id": doc.task_id,
        "file_id": doc.id,
        "status": doc.status,
        "modality": doc.modality,
        "metadata": doc.metadata_json,
    }
