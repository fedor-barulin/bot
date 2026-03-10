import g4f
import logging

class LLMClient:
    """Клиент для взаимодействия с бесплатными LLM через g4f."""
    def __init__(self, model_name=g4f.models.default):
        self.model_name = model_name

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        try:
            response = g4f.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response
        except Exception as e:
            logging.error(f"Error calling LLM {self.model_name}: {e}")
            return ""
