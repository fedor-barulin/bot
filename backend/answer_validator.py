from llm_client import LLMClient

class AnswerValidator:
    """Anti-hallucination механизм проверки ответа."""
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def validate(self, answer: str, context: str) -> str:
        if "Информация отсутствует" in answer:
            return answer

        system_prompt = """
You are an anti-hallucination verification module.
Check the support engineer's response for hallucinations. 
Every fact mentioned in the response MUST be present in the provided context.
If a fact is not found in the context - you must delete it from the response.
If the entire response does not align with the context at all, output strictly: "Информация отсутствует в базе знаний."

All your responses must be in Russian only.
Output ONLY the corrected and verified response, nothing else.
"""
        user_prompt = f"Context:\n{context}\n\nEngineer's response to check:\n{answer}"
        
        validated_answer = self.llm.generate(system_prompt, user_prompt)
        return validated_answer.strip()
