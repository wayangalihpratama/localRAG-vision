import os
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import boto3
from botocore.client import Config
from .worker import process_document
from .config import settings

app = FastAPI(title=settings.PROJECT_NAME)

s3_client = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT,
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
    config=Config(signature_version="s3v4"),
)

# Ensure bucket exists
try:
    s3_client.head_bucket(Bucket=settings.S3_BUCKET)
except Exception:
    s3_client.create_bucket(Bucket=settings.S3_BUCKET)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "LocalRAG Vision API is running", "status": "healthy"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post(
    "/api/v1/ingest/upload", status_code=status.HTTP_202_ACCEPTED
)  # noqa: E501
async def upload_document(file: UploadFile = File(...)):
    # Validate file type
    allowed_types = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # noqa: E501
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
        # Upload to MinIO
        s3_client.upload_fileobj(file.file, settings.S3_BUCKET, s3_key)

        # Trigger Background Task
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
