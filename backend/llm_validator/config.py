# llm_validator/config.py

import os
from typing import Dict
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    # 👇 ВАЖНО: Меняем настройки с облачных на локальные
    deepseek_api_key = "ollama"                          # Можно любую строку
    deepseek_base_url = "http://localhost:11434"         # Адрес твоего сервера Ollama
    deepseek_model = "gpt-oss:120b-cloud"                     # Имя модели, которое ты скачал

    # База данных (оставляем как есть)
    db_config: Dict[str, str] = field(default_factory=lambda: {
        'dbname': os.getenv('DB_NAME', 'lawyer_assistant'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'hello_postgresql!'),
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432')
    })

    temperature: float = 0.1
    request_timeout: int = 120          # Для локальной модели лучше увеличить таймаут
    embedder_model: str = "intfloat/multilingual-e5-large"

    def validate(self):
        # Для Ollama проверка ключа не нужна
        pass