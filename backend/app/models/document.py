from sqlalchemy import Column, String, DateTime, JSON, Enum
from datetime import datetime
import enum
from app.db import Base


class DocumentStatus(str, enum.Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String, index=True)
    s3_key = Column(String, unique=True)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.PROCESSING)
    task_id = Column(String, nullable=True)
    modality = Column(String, default="text")  # "text" or "video"
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
