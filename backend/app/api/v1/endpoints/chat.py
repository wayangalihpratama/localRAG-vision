from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.services.chat_service import chat_service


router = APIRouter()


class ChatRequest(BaseModel):
    query: str


@router.post("/completions")
async def chat_completion(request: ChatRequest):
    try:
        return StreamingResponse(
            chat_service.stream_rag_response(request.query),
            media_type="text/event-stream",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
