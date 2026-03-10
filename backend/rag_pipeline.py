import time
from llm_client import LLMClient
from query_understanding import QueryUnderstanding
from knowledge_router import KnowledgeRouter
from query_rewriter import QueryRewriter
from hybrid_search import HybridSearch
from reranker import Reranker
from context_builder import ContextBuilder
from reasoning_engine import ReasoningEngine
from answer_validator import AnswerValidator

class RAGPipeline:
    """Основной пайплайн RAG Enterprise."""
    def __init__(self, llm_model="llama3", qdrant_host="localhost"):
        self.llm = LLMClient(model_name=llm_model)
        self.query_understanding = QueryUnderstanding(self.llm)
        self.knowledge_router = KnowledgeRouter()
        self.query_rewriter = QueryRewriter(self.llm)
        self.hybrid_search = HybridSearch(qdrant_host=qdrant_host)
        self.reranker = Reranker()
        self.context_builder = ContextBuilder()
        self.reasoning = ReasoningEngine(self.llm)
        self.validator = AnswerValidator(self.llm)

    def process(self, question: str) -> tuple[str, list[dict], float]:
        start_time = time.time()
        
        # 1. Query Understanding
        qa = self.query_understanding.analyze(question)
        
        # 2. Knowledge Routing
        sections = self.knowledge_router.route(qa)
        
        # 3. Query Rewriting
        queries = self.query_rewriter.rewrite(question)
        
        # 4. Hybrid Search
        chunks = self.hybrid_search.search(queries, sections, limit=10)
        
        # 5. Reranking
        ranked_chunks = self.reranker.rerank(question, chunks, top_k=5)
        
        # 6. Context Builder
        context = self.context_builder.build(ranked_chunks)
        
        # 7. Reasoning Engine
        initial_answer = self.reasoning.generate_answer(question, context)
        
        # 8. Answer Validation
        final_answer = self.validator.validate(initial_answer, context)
        
        p_time = time.time() - start_time
        return final_answer, ranked_chunks, p_time
