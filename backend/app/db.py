import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# --- Vector DB (LanceDB) ---
_model = None
_db = None


def get_embedding_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
    return _model


def get_db():
    global _db
    if _db is None:
        import lancedb

        os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)
        _db = lancedb.connect(settings.VECTOR_DB_PATH)
    return _db


# --- SQL DB (SQLite) ---
Base = declarative_base()
_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        url = os.getenv("DATABASE_URL", "sqlite:///./localrag.db")
        print(f"--- INITIALIZING ENGINE with URL: {url} ---")
        _engine = create_engine(url, connect_args={"check_same_thread": False})
    return _engine


def get_session_local():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=get_engine()
        )
    return _SessionLocal


def get_sql_db():
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initializes both LanceDB and SQL tables.
    """
    # 1. Init SQL Tables
    Base.metadata.create_all(bind=get_engine())

    # 2. Init LanceDB
    db = get_db()
    table_name = "knowledge_base"
    return (
        db.open_table(table_name) if table_name in db.table_names() else None
    )
