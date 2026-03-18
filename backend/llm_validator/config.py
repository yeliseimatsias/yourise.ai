"""
Конфигурация модуля llm_validator.

Поддерживает три способа конфигурации (в порядке приоритета):
1. Прямая передача параметров в конструктор
2. Переменные окружения
3. Значения по умолчанию
"""

import os
from typing import Dict, Optional
from dataclasses import dataclass, field


@dataclass
class Config:
    """
    Конфигурация для LLM Validator.
    
    Args:
        deepseek_api_key: API ключ для OpenRouter/DeepSeek
        deepseek_base_url: Базовый URL API
        deepseek_model: Название модели
        db_config: Параметры подключения к БД
        llm_temperature: Температура для генерации (0.0-1.0)
        llm_max_tokens: Максимальное количество токенов
        llm_retries: Количество повторных попыток
        max_concurrent_requests: Лимит параллельных запросов
        request_timeout: Таймаут запроса в секундах
    """
    
    # DeepSeek/OpenRouter настройки
    deepseek_api_key: str = field(default="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")
    deepseek_base_url: str = field(default="https://openrouter.ai/api/v1")
    deepseek_model: str = field(default="deepseek/deepseek-r1")
    
    # Настройки БД
    db_config: Dict[str, str] = field(default_factory=lambda: {
        'dbname': 'lawyer_assistant',
        'user': 'postgres',
        'password': 'hello_postgresql!',
        'host': 'localhost',
        'port': '5432'
    })
    
    # Настройки LLM
    llm_temperature: float = 0.1
    llm_max_tokens: int = 2000
    llm_retries: int = 3
    
    # Лимиты
    max_concurrent_requests: int = 5
    request_timeout: int = 30
    
    def __post_init__(self):
        """Загружает значения из переменных окружения, если не заданы явно."""
        if not self.deepseek_api_key:
            self.deepseek_api_key = os.getenv('DEEPSEEK_API_KEY', '')
        
        if self.deepseek_base_url == "https://openrouter.ai/api/v1":
            self.deepseek_base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://openrouter.ai/api/v1')
        
        if self.deepseek_model == "deepseek/deepseek-r1":
            self.deepseek_model = os.getenv('DEEPSEEK_MODEL', 'deepseek/deepseek-r1')
        
        # Обновляем db_config из env, если есть соответствующие переменные
        env_db_mapping = {
            'dbname': 'DB_NAME',
            'user': 'DB_USER', 
            'password': 'DB_PASSWORD',
            'host': 'DB_HOST',
            'port': 'DB_PORT'
        }
        
        for key, env_var in env_db_mapping.items():
            env_value = os.getenv(env_var)
            if env_value and self.db_config.get(key) == self._get_default_db_value(key):
                self.db_config[key] = env_value
    
    def _get_default_db_value(self, key: str) -> str:
        """Возвращает дефолтное значение для ключа БД."""
        defaults = {
            'dbname': 'yourise',
            'user': 'postgres',
            'password': 'postgres',
            'host': 'localhost',
            'port': '5432'
        }
        return defaults.get(key, '')
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Создает конфигурацию полностью из переменных окружения."""
        return cls()
    
    @classmethod
    def for_testing(cls, api_key: str = "test-key") -> 'Config':
        """Создает тестовую конфигурацию."""
        return cls(
            deepseek_api_key=api_key,
            db_config={'dbname': ':memory:', 'user': '', 'password': '', 'host': '', 'port': ''},
            llm_retries=1
        )
    
    def validate(self) -> bool:
        """Проверяет, что конфигурация валидна."""
        if not self.deepseek_api_key:
            raise ValueError("DEEPSEEK_API_KEY не задан. Передайте в конструктор или установите переменную окружения.")
        return True