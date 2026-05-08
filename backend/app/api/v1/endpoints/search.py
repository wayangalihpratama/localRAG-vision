from fastapi import APIRouter, HTTPException, status
from app.schemas.search import SearchQuery, SearchResponse
from app.services.search_service import search_service

router = APIRouter()


@router.post("/query", response_model=SearchResponse)
async def query_knowledge_base(search_query: SearchQuery):
    try:
        results = search_service.hybrid_search(
            search_query.query, search_query.limit
        )
        return {"results": results}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}",
        )
