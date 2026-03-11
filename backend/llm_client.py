import g4f
import logging

class LLMClient:
    """Клиент для взаимодействия с бесплатными LLM через g4f."""
    def __init__(self, model_name=g4f.models.default):
        self.model_name = model_name

    def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = None) -> str:
        try:
            kwargs = {
                "model": self.model_name or g4f.models.default,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            }
            if max_tokens:
                kwargs["max_tokens"] = max_tokens

            response = g4f.ChatCompletion.create(**kwargs)
            return response
        except Exception as e:
            logging.error(f"Error calling LLM {self.model_name}: {e}")
            return ""
