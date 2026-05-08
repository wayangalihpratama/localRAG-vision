import pytest
from unittest.mock import patch, MagicMock
from app.schemas.search import SearchQuery
from app.api.v1.endpoints.search import query_knowledge_base


@patch("app.api.v1.endpoints.search.search_service")
@pytest.mark.anyio
async def test_search_endpoint(mock_search_service):
    # Mock search results
    mock_search_service.hybrid_search.return_value = [
        {"id": "1", "text": "Result 1", "metadata": {"file": "test.pdf"}}
    ]

    query = SearchQuery(query="test query", limit=1)
    response = await query_knowledge_base(query)

    assert "results" in response
    assert len(response["results"]) == 1
    assert response["results"][0]["text"] == "Result 1"
    mock_search_service.hybrid_search.assert_called_once()
