import lancedb
import os
from sentence_transformers import SentenceTransformer
from app.config import settings

# Lazy-loaded Embedding Model
_model = None


def get_embedding_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
    return _model


# Database Connection
_db = None


def get_db():
    global _db
    if _db is None:
        os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)
        _db = lancedb.connect(settings.VECTOR_DB_PATH)
    return _db


def init_db():
    """
    Initializes the knowledge_base table with the required schema.
    """
    db = get_db()
    table_name = "knowledge_base"

    if table_name not in db.table_names():
        # Schema is implicitly defined by the first data insertion,
        # but we can also pre-define it if needed.
        pass
    return (
        db.open_table(table_name) if table_name in db.table_names() else None
    )
