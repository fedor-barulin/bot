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

    def clear_collection(self):
        existing = [c.name for c in self.client.get_collections().collections]
        if self.collection_name in existing:
            self.client.delete_collection(self.collection_name)
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE),
        )

    def upload_chunks(self, chunks: list[dict]) -> int:
        start_id = self.client.count(collection_name=self.collection_name).count
        encoder = self._get_encoder()
        points = []
        for i, chunk in enumerate(chunks):
            chunk_id = start_id + i
            vector = encoder.encode(chunk["text"]).tolist()
            points.append(models.PointStruct(
                id=chunk_id,
                vector=vector,
                payload={
                    "chunk_id": chunk_id,
                    "title": chunk["title"],
                    "section": chunk["section"],
                    "page": chunk["page"],
                    "tags": chunk["tags"],
                    "text": chunk["text"],
                    "source": chunk["source"],
                },
            ))
        self.client.upsert(collection_name=self.collection_name, points=points)
        return len(points)

    def delete_by_document(self, title: str) -> int:
        """Удаляет все чанки конкретного документа по полю title."""
        result = self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[models.FieldCondition(
                        key="title",
                        match=models.MatchValue(value=title)
                    )]
                )
            ),
        )
        logging.info(f"Deleted chunks for document '{title}': {result}")
        return 1

    def list_documents(self) -> list[str]:
        """Возвращает список уникальных названий документов в базе."""
        result = self.client.scroll(
            collection_name=self.collection_name,
            with_payload=True,
            limit=10000,
        )
        titles = {point.payload.get("title") for point in result[0] if point.payload.get("title")}
        return sorted(titles)

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
