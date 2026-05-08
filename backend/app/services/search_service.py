from app.db import get_db, get_embedding_model


class SearchService:
    def __init__(self):
        self.db = get_db()
        self.model = get_embedding_model()
        self.table_name = "knowledge_base"

    def hybrid_search(self, query: str, limit: int = 5):
        if self.table_name not in self.db.table_names():
            return []

        table = self.db.open_table(self.table_name)
        query_vector = self.model.encode(query)

        results = table.search(query_vector).limit(limit).to_list()
        return results


search_service = SearchService()
