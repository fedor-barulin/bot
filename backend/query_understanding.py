import json
from pydantic import BaseModel
from llm_client import LLMClient

class QueryIntent(BaseModel):
    intent: str
    service: str
    problem_type: str

class QueryUnderstanding:
    """Анализ интента, сервиса и проблемы из вопроса пользователя."""
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def analyze(self, question: str) -> dict:
        system_prompt = """
You are an intent analyzer AI. 
Analyze the user question and extract the following parameters:
- intent (e.g.: troubleshooting, info, billing)
- service (e.g.: mobile internet, sms, voice)
- problem_type (e.g.: connectivity, speed, unknown)

Output ONLY a valid JSON format with these exact keys. Do not include any markdown formatting blocks like ```json, just the raw JSON text.
{"intent": "...", "service": "...", "problem_type": "..."}
"""
        user_prompt = f'Question: "{question}"'
        
        response = self.llm.generate(system_prompt, user_prompt)
        try:
            import re
            json_str = re.search(r'\{.*\}', response.replace('\n', '')).group(0)
            return json.loads(json_str)
        except Exception:
            return {"intent": "unknown", "service": "unknown", "problem_type": "unknown"}
