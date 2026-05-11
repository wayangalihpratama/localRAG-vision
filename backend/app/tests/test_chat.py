import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.chat_service import ChatService


@pytest.mark.anyio
async def test_stream_rag_response(mock_all_services):
    # Setup mocks
    with patch(
        "app.services.chat_service.get_search_service"
    ) as mock_get_search:
        mock_search = MagicMock()
        mock_get_search.return_value = mock_search
        mock_search.hybrid_search.return_value = [
            {"text": "Context piece 1", "metadata": {"file": "doc1.txt"}}
        ]

        # Mock httpx response for streaming
        mock_response = MagicMock()

        # Create an async generator for aiter_lines
        async def mock_aiter():
            yield json.dumps({"response": "Hello", "done": False})
            yield json.dumps({"response": " world", "done": True})

        mock_response.aiter_lines = mock_aiter

        # Mock httpx.AsyncClient context manager
        mock_client = MagicMock()
        mock_client.__aenter__.return_value = mock_client

        # Mock the stream() async context manager
        mock_stream_ctx = MagicMock()
        mock_stream_ctx.__aenter__ = AsyncMock(return_value=mock_response)
        mock_stream_ctx.__aexit__ = AsyncMock()
        mock_client.stream.return_value = mock_stream_ctx

        with patch("httpx.AsyncClient", return_value=mock_client):
            chat_service = ChatService()
            chunks = []
            async for chunk in chat_service.stream_rag_response("Hi"):
                chunks.append(json.loads(chunk.strip()))

            # Verify chunks
            # 1 citations chunk + 2 content chunks
            assert len(chunks) == 3
            assert chunks[0]["type"] == "citations"
            assert chunks[1]["data"] == "Hello"
            assert chunks[2]["data"] == " world"

            mock_search.hybrid_search.assert_called_once()
