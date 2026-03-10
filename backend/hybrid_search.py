from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer

class HybridSearch:
    """Гибридный поиск (Векторный + Keyword) в Qdrant."""
    def __init__(self, qdrant_host="localhost", qdrant_port=6333):
        self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
        # Использование мультиязычной модели embeddings
        self.encoder = SentenceTransformer("BAAI/bge-m3", device="cpu")
        self.collection_name = "knowledge_base"

    def search(self, queries: list[str], sections: list[str], limit=10) -> list[dict]:
        all_results = []
        
        # Фильтрация по разделам из Knowledge Router
        must_conditions = []
        if sections:
            must_conditions.append(
                models.FieldCondition(
                    key="section",
                    match=models.MatchAny(any=sections)
                )
            )

        for query in queries:
            try:
                vector = self.encoder.encode(query).tolist()
                
                # Qdrant search (поддерживает Dense векторы, для BM25 нужно настраивать Sparse векторы в Qdrant)
                # Предполагаем гибридный поиск реализованный через fast hybrid Qdrant, здесь обычный:
                hits = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=vector,
                    query_filter=models.Filter(must=must_conditions) if must_conditions else None,
                    limit=limit
                )
                for hit in hits:
                    all_results.append(hit.payload)
            except Exception as e:
                print(f"HybridSearch error: {e}")
        
        # Дедупликация чанков
        unique_results = {res['chunk_id']: res for res in all_results if 'chunk_id' in res}
        return list(unique_results.values())
