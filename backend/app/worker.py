import os
import tempfile
import boto3
from botocore.client import Config
from celery import Celery
from docling.document_converter import DocumentConverter
from .config import settings

s3_client = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT,
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
    config=Config(signature_version="s3v4"),  # noqa: E501
)

celery_app = Celery(
    "worker", broker=settings.REDIS_URL, backend=settings.REDIS_URL
)

# Lazy-loaded Docling Converter
_converter = None


def get_converter():
    global _converter
    if _converter is None:
        _converter = DocumentConverter()
    return _converter


@celery_app.task(name="process_document")
def process_document(s3_key: str):
    """
    Downloads a document from MinIO and extracts structured content
    using Docling.
    """
    converter = get_converter()
    with tempfile.TemporaryDirectory() as temp_dir:
        local_path = os.path.join(temp_dir, s3_key)

        try:
            # 1. Download from MinIO
            s3_client.download_file(settings.S3_BUCKET, s3_key, local_path)

            # 2. Convert with Docling
            result = converter.convert(local_path)

            # 3. Export to Markdown
            markdown_content = result.document.export_to_markdown()

            # TODO: Add Chunking and Indexing in the next story

            return {
                "status": "completed",
                "file": s3_key,
                "extraction_length": len(markdown_content),
                "preview": markdown_content[:500] if markdown_content else "",
            }

        except Exception as e:
            return {"status": "failed", "file": s3_key, "error": str(e)}
