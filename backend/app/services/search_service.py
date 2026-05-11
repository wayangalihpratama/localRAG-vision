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

        try:
            results = table.search(query_vector.tolist()).limit(limit).to_list()
            return results
        except Exception as e:
            raise Exception(str(e))


_search_service = None


def get_search_service():
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service
