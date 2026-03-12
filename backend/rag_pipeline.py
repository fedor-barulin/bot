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
            max_tokens=1000,
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

Always take into account the full conversation history when answering or asking clarifying questions.

IMPORTANT — follow this decision tree in order:

Step A. Is the question about telecom (services, tariffs, equipment, the company)?
  - NO → respond exactly: "Информация отсутствует в базе знаний". Stop.
  - YES → go to Step B.

Step B. Is the question broad, ambiguous, or could refer to several different things?
  - YES → You MUST ask a short clarifying question listing the possible options. You MAY use general telecom knowledge to understand what the user might mean (e.g., "баланс" can mean monetary balance or remaining package volume). Do NOT answer — only ask. Stop.
  - NO → go to Step C.

Step C. Can the question be answered using ONLY the facts explicitly stated in the CONTEXT below?
  - YES → Answer using ONLY those facts. Do NOT invent, combine, or infer anything not literally written in the context. Each claim must trace back to a single passage.
  - NO → respond exactly: "Информация отсутствует в базе знаний". Stop.

Formatting rules:
- The answer MUST be in Russian.
- Keep answers concise (up to 8 sentences).
- Use bullet points or numbered lists for step-by-step instructions.
- No introductions or filler phrases.

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
            
        # 1. Remove filler phrases
        fillers = ["Конечно", "Вы можете", "Обычно", "Как правило"]
        cleaned_text = text
        for filler in fillers:
            cleaned_text = re.sub(rf"(?i)\b{filler}[,\s]*", "", cleaned_text)
            
        final_answer = cleaned_text.strip()
        
        # Ensure proper capitalization
        if final_answer and final_answer[0].islower():
            final_answer = final_answer[0].upper() + final_answer[1:]
            
        # 2. Final check for empty string
        if not final_answer:
            return "Информация отсутствует в базе знаний"
            
        return final_answer
