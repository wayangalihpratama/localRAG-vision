import boto3
from botocore.client import Config
from app.config import settings


class StorageService:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            config=Config(signature_version="s3v4"),
        )
        self.bucket = settings.S3_BUCKET
        self._ensure_bucket()

    def _ensure_bucket(self):
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except Exception:
            self.client.create_bucket(Bucket=self.bucket)

    def upload_file(self, file_obj, s3_key: str):
        self.client.upload_fileobj(file_obj, self.bucket, s3_key)
        return s3_key

    def download_file(self, s3_key: str, local_path: str):
        self.client.download_file(self.bucket, s3_key, local_path)
        return local_path

    def delete_file(self, s3_key: str):
        self.client.delete_object(Bucket=self.bucket, Key=s3_key)
        return s3_key


storage_service = StorageService()
