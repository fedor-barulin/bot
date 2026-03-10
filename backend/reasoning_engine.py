from llm_client import LLMClient

class ReasoningEngine:
    """Мульти-документный Reasoning."""
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def generate_answer(self, question: str, context: str) -> str:
        system_prompt = f"""
You are an expert technical support engineer for a telecom operator.
All responses must be in Russian.
Answer strictly and professionally ONLY based on the provided context.
If the information is not present in the context, your ONLY response should be: "Информация отсутствует в базе знаний." (do not write anything else).

YOUR RESPONSE MUST HAVE THE FOLLOWING STRUCTURE:
**Краткое объяснение:** [Brief explanation]
**Возможные причины:** [Possible causes listed]
**Шаги диагностики:** [1. 2. 3...]
**Решение:** [Instruction]

Context:
{context}
"""
        user_prompt = f"User question: {question}\n\nFormulate the answer based on the context."
        return self.llm.generate(system_prompt, user_prompt)
