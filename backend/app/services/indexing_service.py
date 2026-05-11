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
            table = self.db.create_table(self.table_name, data=data)

        # Create/Update FTS index for keyword search
        table.create_fts_index("text", replace=True)

        return len(chunks)

    def index_video(
        self,
        s3_key: str,
        segments: list,
        visual_descriptions: list,
        audio_transcripts: list = None,
    ):
        """
        Indexes video segments with visual descriptions and
        optional transcripts.
        """
        if not audio_transcripts:
            audio_transcripts = [""] * len(segments)

        # 1. Prepare Narrative Chunks
        narratives = []
        for visual, audio in zip(visual_descriptions, audio_transcripts):
            narrative = f"{visual} {audio}".strip()
            narratives.append(narrative)

        if not narratives:
            return 0

        # 2. Embedding
        vectors = self.model.encode(narratives)

        # 3. LanceDB Indexing
        data = []
        for i, (narrative, vector, segment) in enumerate(
            zip(narratives, vectors, segments)
        ):
            start_sec, end_sec = segment
            data.append(
                {
                    "id": f"{s3_key}_{i}",
                    "vector": vector.tolist(),
                    "text": narrative,
                    "metadata": {
                        "file": s3_key,
                        "modality": "video",
                        "start_time": start_sec,
                        "end_time": end_sec,
                    },
                }
            )

        if self.table_name in self.db.table_names():
            table = self.db.open_table(self.table_name)
            table.add(data)
        else:
            table = self.db.create_table(self.table_name, data=data)

        # Create/Update FTS index
        table.create_fts_index("text", replace=True)

        return len(narratives)


_indexing_service = None


def get_indexing_service():
    global _indexing_service
    if _indexing_service is None:
        _indexing_service = IndexingService()
    return _indexing_service
