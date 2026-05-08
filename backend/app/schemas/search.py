from pydantic import BaseModel
from typing import List, Optional, Any


class SearchQuery(BaseModel):
    query: str
    limit: int = 5


class SearchResult(BaseModel):
    id: str
    text: str
    metadata: Optional[Any] = None
    _distance: Optional[float] = None


class SearchResponse(BaseModel):
    results: List[SearchResult]
