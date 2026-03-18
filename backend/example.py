#!/usr/bin/env python3
"""
Пример использования LLM Validator.

Демонстрирует различные сценарии использования модуля.
"""

import json
import logging
from llm_validator import LLMValidator, Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_1_basic_usage():
    """Пример 1: Базовое использование."""
    print("\n" + "="*60)
    print("Пример 1: Базовая проверка изменения")
    print("="*60)
    
    # Конфигурация (API ключ можно передать напрямую или через env)
    config = Config(
        deepseek_api_key="sk-or-v1-...",  # Замените на ваш ключ
        llm_temperature=0.1,
        llm_retries=3
    )
    
    # Данные для проверки (пример с противоречием)
    change_data = {
        "change_id": "vacation-001",
        "session_id": "session-001",
        "type": "modified",
        "element_number": "5.3",
        "old_text": "Работник имеет право на отпуск продолжительностью 24 календарных дня.",
        "new_text": "Работнику предоставляется отпуск продолжительностью 21 календарный день.",
        "full_chunk": "Статья 5. Права работника\n5.3. Работнику предоставляется отпуск продолжительностью 21 календарный день.",
        "document_type": "local_act",
        "document_level": 7,
        "relevant_laws": [
            {
                "law_reference": "Трудовой кодекс РБ, ст.155",
                "chunk_text": "Статья 155. Продолжительность основного отпуска\nОсновной отпуск предоставляется продолжительностью не менее 24 календарных дней.",
                "similarity": 0.89,
                "hierarchy_level": 2
            }
        ]
    }
    
    with LLMValidator(config) as validator:
        result = validator.validate_change(change_data)
        
        print(f"\nРезультат проверки:")
        print(f"  ID изменения: {result.change_id}")
        print(f"  Общий риск: {result.overall_risk.upper()}")
        print(f"  Пояснение: {result.overall_explanation}")
        print(f"  Проверено законов: {result.total_laws_checked}")
        print(f"  Противоречий найдено: {result.contradictions_found}")
        
        if result.validation_results:
            vr = result.validation_results[0]
            print(f"\n  Детали:")
            print(f"    Закон: {vr['law_reference']}")
            print(f"    Тип противоречия: {vr['contradiction_type']}")
            print(f"    Уверенность: {vr['confidence']:.0%}")
            print(f"    Серьезность: {vr['severity']}")
            print(f"    Пояснение: {vr['explanation'][:100]}...")
            if vr['suggestion']:
                print(f"    Рекомендация: {vr['suggestion']}")


def example_2_no_contradiction():
    """Пример 2: Проверка без противоречий."""
    print("\n" + "="*60)
    print("Пример 2: Проверка без противоречий")
    print("="*60)
    
    config = Config(deepseek_api_key="sk-or-v1-...")
    
    # Данные без противоречий
    change_data = {
        "change_id": "schedule-001",
        "session_id": "session-001",
        "type": "added",
        "element_number": "5.5",
        "old_text": "",
        "new_text": "График отпусков утверждается нанимателем не позднее чем за две недели до начала календарного года.",
        "full_chunk": "Статья 5. Права работника\n5.5. График отпусков утверждается нанимателем не позднее чем за две недели до начала календарного года.",
        "document_type": "local_act",
        "document_level": 7,
        "relevant_laws": [
            {
                "law_reference": "Трудовой кодекс РБ, ст.168",
                "chunk_text": "Статья 168. Очередность предоставления отпусков\nОтпуск предоставляется в соответствии с графиком отпусков.",
                "similarity": 0.75,
                "hierarchy_level": 2
            }
        ]
    }
    
    with LLMValidator(config) as validator:
        result = validator.validate_change(change_data)
        
        print(f"\nРезультат: {result.overall_risk.upper()}")
        print(f"Пояснение: {result.overall_explanation}")


def example_3_multiple_laws():
    """Пример 3: Проверка по нескольким законам."""
    print("\n" + "="*60)
    print("Пример 3: Проверка по нескольким законам")
    print("="*60)
    
    config = Config(deepseek_api_key="sk-or-v1-...")
    
    change_data = {
        "change_id": "multi-001",
        "session_id": "session-001",
        "type": "modified",
        "element_number": "3.1",
        "old_text": "Зарплата выплачивается 2 раза в месяц.",
        "new_text": "Зарплата выплачивается 1 раз в месяц.",
        "full_chunk": "Статья 3. Оплата труда\n3.1. Зарплата выплачивается 1 раз в месяц.",
        "document_type": "local_act",
        "document_level": 7,
        "relevant_laws": [
            {
                "law_reference": "Трудовой кодекс РБ, ст.59",
                "chunk_text": "Статья 59. Сроки выплаты заработной платы\nЗаработная плата выплачивается не реже чем два раза в месяц.",
                "similarity": 0.92,
                "hierarchy_level": 2
            },
            {
                "law_reference": "Конституция РБ, ст.42",
                "chunk_text": "Статья 42. Каждый имеет право на благоприятные условия труда...",
                "similarity": 0.45,
                "hierarchy_level": 1
            }
        ]
    }
    
    with LLMValidator(config) as validator:
        # Используем параллельную обработку для скорости
        result = validator.validate_change_parallel(change_data, max_workers=2)
        
        print(f"\nРезультат: {result.overall_risk.upper()}")
        print(f"Проверено законов: {result.total_laws_checked}")
        
        for vr in result.validation_results:
            print(f"\n  {vr['law_reference']}:")
            print(f"    Тип: {vr['contradiction_type']}")
            print(f"    Уверенность: {vr['confidence']:.0%}")


def example_4_batch_processing():
    """Пример 4: Пакетная обработка с прогрессом."""
    print("\n" + "="*60)
    print("Пример 4: Пакетная обработка")
    print("="*60)
    
    config = Config(deepseek_api_key="sk-or-v1-...")
    
    changes = [
        {
            "change_id": "batch-001",
            "session_id": "batch-session",
            "type": "modified",
            "old_text": "Отпуск 24 дня",
            "new_text": "Отпуск 21 день",
            "full_chunk": "Статья 5. Отпуск 21 день",
            "relevant_laws": [
                {
                    "law_reference": "ТК РБ, ст.155",
                    "chunk_text": "Отпуск не менее 24 дней",
                    "similarity": 0.9,
                    "hierarchy_level": 2
                }
            ]
        },
        {
            "change_id": "batch-002",
            "session_id": "batch-session",
            "type": "added",
            "old_text": "",
            "new_text": "Работник обязан соблюдать трудовую дисциплину",
            "full_chunk": "Статья 6. Дисциплина",
            "relevant_laws": [
                {
                    "law_reference": "ТК РБ, ст.10",
                    "chunk_text": "Работник обязан добросовестно выполнять свои трудовые обязанности",
                    "similarity": 0.8,
                    "hierarchy_level": 2
                }
            ]
        }
    ]
    
    def on_progress(current, total):
        print(f"  Прогресс: {current}/{total}")
    
    with LLMValidator(config) as validator:
        results = validator.validate_batch(changes, progress_callback=on_progress)
        
        print("\nИтоги:")
        for r in results:
            print(f"  {r.change_id}: {r.overall_risk}")
        
        # Статистика сессии
        stats = validator.db.get_session_stats("batch-session")
        print(f"\nСтатистика сессии:")
        print(f"  Red: {stats['red']}, Yellow: {stats['yellow']}, Green: {stats['green']}")


def example_5_simple_function():
    """Пример 5: Использование упрощенной функции."""
    print("\n" + "="*60)
    print("Пример 5: Упрощенная функция validate_single_change")
    print("="*60)
    
    from llm_validator.main import validate_single_change
    
    change_data = {
        "change_id": "simple-001",
        "type": "modified",
        "old_text": "Старый текст",
        "new_text": "Новый текст",
        "full_chunk": "Контекст",
        "relevant_laws": [
            {
                "law_reference": "Закон",
                "chunk_text": "Текст закона",
                "similarity": 0.8,
                "hierarchy_level": 2
            }
        ]
    }
    
    # Простой вызов одной функцией
    result = validate_single_change(
        change_data=change_data,
        api_key="sk-or-v1-..."
    )
    
    print(f"\nРезультат: {result['overall_risk']}")
    print(f"JSON: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}...")


def example_6_database_operations():
    """Пример 6: Работа с базой данных."""
    print("\n" + "="*60)
    print("Пример 6: Работа с базой данных")
    print("="*60)
    
    # from llm_validator.db import ValidatorRepository
    
    # SQLite in-memory для тестирования
    # repo = ValidatorRepository({'dbname': ':memory:'})
    
    # Сохраняем результат
    # result_id = repo.save_validation(
    #     change_id="test-001",
    #     law_reference="ТК РБ, ст.155",
    #     law_text="Текст закона",
    #     contradiction_type="direct",
    #     explanation="Прямое противоречие",
    #     confidence=0.95,
    #     is_contradiction=True,
    #     quote_from_law="не менее 24 дней",
    #     suggestion="Исправить на 24 дня",
    #     severity="high"
    # )
    # print(f"\nСохранен результат с ID: {result_id}")
    
    # Получаем валидации для изменения
    # validations = repo.get_validations_by_change("test-001")
    # print(f"Найдено валидаций: {len(validations)}")
    
    # Обновляем риск
    # repo.update_change_risk(
    #     change_id="test-001",
    #     overall_risk="red",
    #     session_id="session-001",
    #     explanation="Обнаружено прямое противоречие"
    # )
    
    # Получаем риск
    # risk = repo.get_change_risk("test-001")
    # print(f"Риск изменения: {risk['overall_risk']}")
    # 
    # repo.close()


def main():
    """Запускает все примеры."""
    print("\n" + "="*60)
    print("LLM Validator - Примеры использования")
    print("="*60)
    
    # Замените на ваш реальный API ключ для тестирования
    api_key = "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"
    
    try:
        # Примеры без реальных API вызовов
        example_6_database_operations()
        
        # Примеры с API (закомментированы, требуют реальный ключ)
        example_1_basic_usage()
        # example_2_no_contradiction()
        # example_3_multiple_laws()
        # example_4_batch_processing()
        # example_5_simple_function()
        
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        raise


if __name__ == "__main__":
    main()
