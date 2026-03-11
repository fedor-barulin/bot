from llm_client import LLMClient

MAX_CONTEXT_FOR_VALIDATION = 3000

class AnswerValidator:
    """Anti-hallucination механизм проверки ответа."""
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def validate(self, answer: str, context: str) -> str:
        if not answer.strip():
            return "Информация отсутствует в базе знаний"

        if "Информация отсутствует" in answer:
            return answer

        truncated_context = context[:MAX_CONTEXT_FOR_VALIDATION] + "..." if len(context) > MAX_CONTEXT_FOR_VALIDATION else context

        system_prompt = """
You are an anti-hallucination verification module.
Check the support engineer's response for hallucinations.
Every fact mentioned in the response MUST be present in the provided context.
If the answer contains information not present in the context, you must output strictly:
"Информация отсутствует в базе знаний"

All your responses must be in Russian only.
Output ONLY the verified response, nothing else. Do not explain.
"""
        user_prompt = f"Context:\n{truncated_context}\n\nEngineer's response to check:\n{answer}"

        validated_answer = self.llm.generate(system_prompt, user_prompt, max_tokens=200)

        if not validated_answer.strip():
            return answer

        return validated_answer.strip()
