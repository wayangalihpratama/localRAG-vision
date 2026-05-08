import json
import httpx
from typing import AsyncGenerator
from app.config import settings
from app.services.search_service import get_search_service


class ChatService:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL

    async def stream_rag_response(
        self, query: str
    ) -> AsyncGenerator[str, None]:
        # 1. Retrieve Context
        results = get_search_service().hybrid_search(query, limit=3)
        context = "\n\n".join(
            [f"Source [{i+1}]: {r['text']}" for i, r in enumerate(results)]
        )

        # 2. Prepare Citations Metadata
        citations = [
            {"id": i + 1, "text": r["text"], "metadata": r.get("metadata", {})}
            for i, r in enumerate(results)
        ]

        # 3. Construct Prompt
        prompt = f"""
        You are a helpful assistant for LocalRAG Vision.
        Use the following context to answer the user's question.
        If the answer is not in the context, say you don't know.
        Always cite your sources using [1], [2], etc.

        CONTEXT:
        {context}

        USER QUESTION:
        {query}

        ANSWER:
        """

        # 4. Stream from Ollama
        async with httpx.AsyncClient(timeout=120.0) as client:
            # First, send the citations metadata as a structured JSON object
            yield json.dumps({"type": "citations", "data": citations}) + "\n"

            # Then, stream the content
            async with client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": True},
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        chunk = data.get("response", "")
                        yield json.dumps(
                            {"type": "content", "data": chunk}
                        ) + "\n"
                        if data.get("done"):
                            break


_chat_service = None


def get_chat_service():
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
