import pytest
from unittest.mock import patch, MagicMock
from app.schemas.search import SearchQuery
from app.api.v1.endpoints.search import query_knowledge_base


@patch("app.api.v1.endpoints.search.get_search_service")
@pytest.mark.anyio
async def test_search_endpoint(mock_get_search):
    mock_search = MagicMock()
    mock_get_search.return_value = mock_search

    # Mock search results
    mock_search.hybrid_search.return_value = [
        {"id": "1", "text": "Result 1", "metadata": {"file": "test.pdf"}}
    ]

    query = SearchQuery(query="test query", limit=1)
    response = await query_knowledge_base(query)

    assert "results" in response
    assert len(response["results"]) == 1
    assert response["results"][0]["text"] == "Result 1"
    mock_search.hybrid_search.assert_called_once()
