from llm_client import LLMClient

class QueryRewriter:
    """Перефразирование пользовательского запроса для лучшего поиска."""
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def rewrite(self, question: str) -> list[str]:
        system_prompt = """
You are a helpful AI designed to improve search queries for a vector database containing telecom technical support knowledge.
Rewrite the upcoming user question into 3 separate, distinct search queries that contain key terms for better retrieval.
All output responses must be in Russian language only.

Output ONLY the rewritten variants, one per line, without numbering and without any other text.
"""
        user_prompt = f'Question: "{question}"'
        
        response = self.llm.generate(system_prompt, user_prompt)
        queries = [q.strip("- ") for q in response.strip().split('\n') if q.strip()]
        
        # Добавляем оригинальный вопрос для максимального покрытия
        all_queries = [question] + queries
        return all_queries[:4]
