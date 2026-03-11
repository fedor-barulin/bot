from llm_client import LLMClient

class ReasoningEngine:
    """Мульти-документный Reasoning."""
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def generate_answer(self, question: str, context: str) -> str:
        system_prompt = f"""
You are a telecom technical support assistant helping employees.

Your job is to provide short, accurate answers based ONLY on the provided context.

Rules:
* Use ONLY the information from the context.
* Do NOT add information that is not present in the context.
* Do NOT explain general telecom concepts.
* Be concise and technical.
* Maximum 5 sentences.
* If the answer is not in the context, respond exactly with:
"Информация отсутствует в базе знаний"

The answer MUST be written in Russian.

ANSWER FORMAT:
You must produce answers in one of the following formats:

FOR INSTRUCTIONS:
Название услуги:

1. шаг
2. шаг
3. шаг

Источник: [Название документа и раздела] (URL: [ссылка из контекста, если есть])

FOR INFORMATION:
Краткий ответ (1–2 предложения).

Источник: [Название документа и раздела] (URL: [ссылка из контекста, если есть])

CONTEXT:
{context}

QUESTION:
{question}

ANSWER (Russian only):
"""
        return self.llm.generate(system_prompt, "", max_tokens=200)
