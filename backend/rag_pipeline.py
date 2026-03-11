import time
from llm_client import LLMClient
from knowledge_router import KnowledgeRouter
from hybrid_search import HybridSearch
from reranker import Reranker
from context_builder import ContextBuilder
from reasoning_engine import ReasoningEngine

class RAGPipeline:
    """Основной пайплайн RAG Enterprise."""
    def __init__(self, llm_model="", qdrant_host="localhost"):
        self.llm = LLMClient(model_name=llm_model)
        self.knowledge_router = KnowledgeRouter()
        self.hybrid_search = HybridSearch(qdrant_host=qdrant_host)
        self.reranker = Reranker()
        self.context_builder = ContextBuilder()
        self.reasoning = ReasoningEngine(self.llm)

    def process(self, question: str) -> tuple[str, list[dict], float]:
        start_time = time.time()

        # 1. Knowledge Routing (no LLM needed — router uses heuristics)
        sections = self.knowledge_router.route({})

        # 2. Hybrid Search (original question only)
        chunks = self.hybrid_search.search([question], sections, limit=10)

        # 3. Reranking
        ranked_chunks = self.reranker.rerank(question, chunks, top_k=5)

        # 4. Context Builder
        context = self.context_builder.build(ranked_chunks)

        # 5. Reasoning Engine (single LLM call)
        answer = self.reasoning.generate_answer(question, context)

        if not answer.strip():
            answer = "Информация отсутствует в базе знаний."

        p_time = time.time() - start_time
        return answer, ranked_chunks, p_time
