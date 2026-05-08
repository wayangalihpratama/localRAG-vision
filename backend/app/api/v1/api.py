from fastapi import APIRouter
from app.api.v1.endpoints import ingest, search, chat

api_router = APIRouter()

api_router.include_router(ingest.router, prefix="/ingest", tags=["ingestion"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
