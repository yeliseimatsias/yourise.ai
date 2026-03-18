import os
from typing import Dict
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    deepseek_api_key: str = field(default_factory=lambda: os.getenv("DEEPSEEK_API_KEY", ""))
    deepseek_base_url: str = "https://openrouter.ai/api/v1"
    deepseek_model: str = "deepseek/deepseek-r1"

    db_config: Dict[str, str] = field(default_factory=lambda: {
        'dbname': os.getenv('DB_NAME', 'lawyer_assistant'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'hello_postgresql!'),
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432')
    })

    temperature: float = 0.1
    request_timeout: int = 45
    embedder_model: str = "intfloat/multilingual-e5-large"

    def validate(self):
        if not self.deepseek_api_key:
            raise ValueError("API ключ DeepSeek (DEEPSEEK_API_KEY) не задан в .env файле!")