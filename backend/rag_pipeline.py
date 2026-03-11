import time
import logging
import re
from functools import lru_cache
from llm_client import LLMClient
from hybrid_search import HybridSearch

class RAGPipeline:
    """Оптимизированный пайплайн RAG по новой архитектуре."""
    
    def __init__(self, llm_model="llama3", qdrant_host="localhost"):
        self.llm = LLMClient(model_name=llm_model)
        self.hybrid_search = HybridSearch(qdrant_host=qdrant_host)
        

    @lru_cache(maxsize=1000)
    def _cached_search(self, question: str):
        # Retrieve only top_k = 3 chunks
        return self.hybrid_search.search(queries=[question], sections=[], limit=3)

    def process(self, question: str, history: list[dict] = None) -> tuple[str, list[dict], float]:
        start_time = time.time()
        history = history or []
        
        # 1. Vector Search (top_k = 3, cached)
        chunks = self._cached_search(question)
        
        # 2. Prompt Builder (limit context size)
        context = self._build_context(chunks)
        
        # 3. LLM Request (single optimized call with limited tokens)
        system_prompt = self._build_system_prompt(context)
        initial_answer = self.llm.generate(
            system_prompt=system_prompt, 
            user_prompt=question, 
            max_tokens=150,
            history=history
        )
        
        # 4. Lightweight response cleanup
        final_answer = self._clean_response(initial_answer)
        
        p_time = time.time() - start_time
        return final_answer, chunks, p_time

    def _build_context(self, chunks: list[dict]) -> str:
        # Limit context size to avoid sending large context (~1200 tokens or ~4500 chars)
        context_parts = []
        total_chars = 0
        MAX_CHARS = 4500
        
        for chunk in chunks[:3]:
            text = chunk.get("text", "")
            if not text:
                continue
                
            if total_chars + len(text) > MAX_CHARS:
                text = text[:MAX_CHARS - total_chars] + "..."
            
            context_parts.append(text)
            total_chars += len(text)
            if total_chars >= MAX_CHARS:
                break
                
        return "\n\n".join(context_parts)

    def _build_system_prompt(self, context: str) -> str:
        return f"""You are a telecom technical support assistant helping employees.

Rules:
1. Answer the user's question, taking into account the conversation history.
2. If the user asks a telecom question but it is too broad, ambiguous, or lacks specific details to give an exact answer (e.g., asking for an office without specifying the city), you MUST ask a short clarifying question instead of failing.
3. If the user asks a specific technical telecom question, use ONLY the information from the provided context.
4. If the user engages in general conversation, logic or casual chat (e.g. asking to pick a word out of a list), you may respond using your general knowledge.
5. Keep the answer concise.
6. Maximum 4 sentences.
7. Avoid introductions and explanations.
8. If the answer to a specific telecom question is not in the context and cannot be clarified, respond exactly with:
"Информация отсутствует в базе знаний"

The answer MUST be written in Russian.

CONTEXT:
{context}"""

    def _clean_response(self, text: str) -> str:
        # Convert to string in case API returns an object
        if type(text) is not str:
            try:
                text = str(text)
            except Exception:
                text = ""

        if not text.strip() or "Информация отсутствует" in text:
            return "Информация отсутствует в базе знаний"
            
        # 1. Remove filler phrases (unnecessary string processing avoided by keeping it simple)
        fillers = ["Конечно", "Вы можете", "Обычно", "Как правило"]
        cleaned_text = text
        for filler in fillers:
            cleaned_text = re.sub(rf"(?i)\b{filler}[,\s]*", "", cleaned_text)
            
        # 2. Trim response to maximum 4 sentences
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', cleaned_text) if s.strip()]
        if len(sentences) > 4:
            sentences = sentences[:4]
            
        final_answer = " ".join(sentences).strip()
        
        # Ensure proper capitalization
        if final_answer and final_answer[0].islower():
            final_answer = final_answer[0].upper() + final_answer[1:]
            
        # 3. Final check for empty string
        if not final_answer:
            return "Информация отсутствует в базе знаний"
            
        return final_answer
