from FlagEmbedding import FlagReranker

class Reranker:
    """Cross-Encoder Reranking найденных чанков."""
    def __init__(self):
        # Использование cross-encoder
        self.reranker = FlagReranker('BAAI/bge-reranker-large', use_fp16=True)
    
    def rerank(self, question: str, chunks: list[dict], top_k=5) -> list[dict]:
        if not chunks:
            return []
        
        pairs = [[question, chunk.get("text", "")] for chunk in chunks]
        scores = self.reranker.compute_score(pairs)
        
        # Защита от одного элемента
        if isinstance(scores, float):
            scores = [scores]
            
        # Сортировка по скору
        ranked = sorted(zip(scores, chunks), key=lambda x: x[0], reverse=True)
        ranked_chunks = [chunk for _, chunk in ranked]
        
        return ranked_chunks[:top_k]
