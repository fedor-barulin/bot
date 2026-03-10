import os
import logging
from qdrant_client import QdrantClient
from qdrant_client.http import models

QDRANT_LOCAL_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "qdrant_storage")

class HybridSearch:
    """Гибридный поиск (Векторный + Keyword) в Qdrant."""
    def __init__(self, qdrant_host="localhost", qdrant_port=6333):
        use_local = os.getenv("QDRANT_HOST") is None
        if use_local:
            self.client = QdrantClient(path=QDRANT_LOCAL_PATH)
        else:
            self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
        self._encoder = None
        self.collection_name = "knowledge_base"

    def _get_encoder(self):
        if self._encoder is None:
            from sentence_transformers import SentenceTransformer
            logging.info("Loading BAAI/bge-m3 encoder...")
            self._encoder = SentenceTransformer("BAAI/bge-m3", device="cpu")
            logging.info("Encoder loaded.")
        return self._encoder

    def search(self, queries: list[str], sections: list[str], limit=10) -> list[dict]:
        all_results = []

        must_conditions = []
        if sections:
            must_conditions.append(
                models.FieldCondition(
                    key="title",
                    match=models.MatchAny(any=sections)
                )
            )

        encoder = self._get_encoder()
        for query in queries:
            try:
                vector = encoder.encode(query).tolist()
                result = self.client.query_points(
                    collection_name=self.collection_name,
                    query=vector,
                    query_filter=models.Filter(must=must_conditions) if must_conditions else None,
                    limit=limit,
                    with_payload=True
                )
                for hit in result.points:
                    all_results.append(hit.payload)
            except Exception as e:
                logging.error(f"HybridSearch error: {e}")

        unique_results = {res['chunk_id']: res for res in all_results if 'chunk_id' in res}
        return list(unique_results.values())
