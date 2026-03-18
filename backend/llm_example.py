#!/usr/bin/env python3
"""
Простой пример использования LLM Validator.
Адаптирован под реальную архитектуру проекта.
"""

import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from llm_validator.config import Config
from llm_validator.main import LLMValidator
from llm_validator.db.validator_repository import ValidatorRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database():
    """Тест работы с БД"""
    print("\n" + "="*60)
    print("Тест работы с БД")
    print("="*60)

    db_params = {
        'dbname': 'lawyer_assistant',
        'user': 'postgres',
        'password': 'hello_postgresql!',
        'host': 'localhost',
        'port': '5432'
    }
    
    # Создаем репозиторий
    repo = ValidatorRepository(db_config=db_params)
    
    # Сохраняем результат (ТОЛЬКО нужные поля!)
    result_id = repo.save_validation(
        change_id="550e8400-e29b-41d4-a716-446655440000",
        law_reference="ТК РБ, ст.155",
        law_text="Основной отпуск предоставляется продолжительностью не менее 24 календарных дней.",
        explanation="Прямое противоречие: в тексте 21 день",
        confidence=0.95
    )
    
    print(f"✅ Сохранен результат с ID: {result_id}")
    repo.close()

def test_validator():
    """Тест валидатора (если он реализован)"""
    print("\n" + "="*60)
    print("Тест валидатора")
    print("="*60)
    
    # Конфиг
    config = Config(deepseek_api_key="your-key-here")
    
    # Данные для проверки
    change_data = {
        "change_id": "vacation-001",
        "new_text": "Работнику предоставляется отпуск 21 день",
        "full_chunk": "Статья 5. Работнику предоставляется отпуск 21 день",
        "relevant_laws": [
            {
                "law_reference": "ТК РБ, ст.155",
                "chunk_text": "Отпуск не менее 24 дней",
                "similarity": 0.89
            }
        ]
    }
    
    # Используем валидатор
    validator = LLMValidator(config)
    try:
        result = validator.validate_change(change_data)
        print(f"Результат: {result}")
    finally:
        validator.close()

def main():
    print("\n" + "="*60)
    print("LLM Validator - Простые тесты")
    print("="*60)
    
    # Тестируем БД
    test_database()
    
    # Тестируем валидатор (закомментировано, т.к. нужен ключ)
    # test_validator()

if __name__ == "__main__":
    main()