from app.db import get_db, get_embedding_model


class IndexingService:
    def __init__(self):
        self.db = get_db()
        self.model = get_embedding_model()
        self.table_name = "knowledge_base"

    def index_markdown(self, s3_key: str, markdown_content: str):
        # 1. Chunking
        chunks = [
            p.strip() for p in markdown_content.split("\n\n") if p.strip()
        ]

        if not chunks:
            return 0

        # 2. Embedding
        vectors = self.model.encode(chunks)

        # 3. LanceDB Indexing
        data = []
        for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
            data.append(
                {
                    "id": f"{s3_key}_{i}",
                    "vector": vector.tolist(),
                    "text": chunk,
                    "metadata": {"file": s3_key, "modality": "text"},
                }
            )

        if self.table_name in self.db.table_names():
            table = self.db.open_table(self.table_name)
            table.add(data)
        else:
            self.db.create_table(self.table_name, data=data)

        return len(chunks)


_indexing_service = None


def get_indexing_service():
    global _indexing_service
    if _indexing_service is None:
        _indexing_service = IndexingService()
    return _indexing_service
