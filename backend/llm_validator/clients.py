import requests
import logging

logger = logging.getLogger(__name__)

class DeepSeekClient:
    def __init__(self, api_key: str, base_url: str, model: str, timeout: int):
        self.headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        self.base_url = base_url
        self.model = model
        self.timeout = timeout

    def generate(self, prompt: str, temperature: float) -> str:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "response_format": {"type": "json_object"}
        }
        try:
            response = requests.post(
               f"{self.base_url}/v1/chat/completions", headers=self.headers, json=payload, timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Ошибка вызова LLM: {e}")
            return "{}"