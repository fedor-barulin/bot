import logging

class Reranker:
    """Cross-Encoder Reranking найденных чанков."""
    def __init__(self):
        self._reranker = None

    def _get_reranker(self):
        if self._reranker is None:
            from FlagEmbedding import FlagReranker
            logging.info("Loading BAAI/bge-reranker-large...")
            self._reranker = FlagReranker('BAAI/bge-reranker-large', use_fp16=True)
            logging.info("Reranker loaded.")
        return self._reranker

    def rerank(self, question: str, chunks: list[dict], top_k=5) -> list[dict]:
        if not chunks:
            return []

        try:
            reranker = self._get_reranker()
            pairs = [[question, chunk.get("text", "")] for chunk in chunks]
            scores = reranker.compute_score(pairs)

            if isinstance(scores, float):
                scores = [scores]

            ranked = sorted(zip(scores, chunks), key=lambda x: x[0], reverse=True)
            return [chunk for _, chunk in ranked][:top_k]
        except Exception as e:
            logging.error(f"Reranker error: {e}")
            return chunks[:top_k]
