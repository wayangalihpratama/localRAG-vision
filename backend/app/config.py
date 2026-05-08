import os
from dataclasses import dataclass


@dataclass
class Settings:
    # Redis / Celery
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")

    # MinIO / S3
    S3_ENDPOINT: str = os.getenv("S3_ENDPOINT", "http://minio:9000")
    S3_ACCESS_KEY: str = os.getenv("S3_ACCESS_KEY", "minioadmin")
    S3_SECRET_KEY: str = os.getenv("S3_SECRET_KEY", "minioadmin")
    S3_BUCKET: str = os.getenv("S3_BUCKET", "raw-documents")

    # Vector DB
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "/app/data/lancedb")
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-small-en-v1.5"

    # Project Settings
    PROJECT_NAME: str = "LocalRAG Vision"
    API_V1_STR: str = "/api/v1"


settings = Settings()
