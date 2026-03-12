import g4f
import logging

class LLMClient:
    """Клиент для взаимодействия с бесплатными LLM через g4f."""
    def __init__(self, model_name=g4f.models.default):
        self.model_name = model_name

    def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = None, history: list[dict] = None) -> str:
        try:
            messages = [{"role": "system", "content": system_prompt}]
            if history:
                messages.extend(history)
            messages.append({"role": "user", "content": user_prompt})
            
            kwargs = {
                "model": self.model_name or g4f.models.default,
                "messages": messages,
                "stream": False,
            }
            if max_tokens:
                kwargs["max_tokens"] = max_tokens

            response = g4f.ChatCompletion.create(**kwargs)

            if isinstance(response, str):
                return response
            try:
                return "".join(str(chunk) for chunk in response)
            except Exception:
                return str(response)
        except Exception as e:
            logging.error(f"Error calling LLM {self.model_name}: {e}")
            return ""
