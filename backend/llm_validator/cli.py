#!/usr/bin/env python3
"""
CLI для LLM Validator.

Использование:
    llm-validate --test
    llm-validate --change-id <id>
    llm-validate --session-id <id>
    llm-validate --file changes.json
"""

import argparse
import json
import sys
import logging
from pathlib import Path

from llm_validator import LLMValidator, Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_changes_from_file(filepath: str) -> list:
    """Загружает изменения из JSON файла."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Поддержка как списка, так и одиночного объекта
        return data if isinstance(data, list) else [data]


def print_result(result: dict):
    """Красивый вывод результата."""
    risk_colors = {
        'red': '\033[91m',      # Красный
        'yellow': '\033[93m',   # Желтый
        'green': '\033[92m',    # Зеленый
        'reset': '\033[0m'
    }
    
    risk = result.get('overall_risk', 'unknown')
    color = risk_colors.get(risk, '')
    reset = risk_colors['reset']
    
    print(f"\n{'='*60}")
    print(f"Изменение: {result['change_id']}")
    print(f"Риск: {color}{risk.upper()}{reset}")
    print(f"Пояснение: {result['overall_explanation']}")
    print(f"Проверено законов: {result['total_laws_checked']}")
    print(f"Противоречий: {result['contradictions_found']}")
    print(f"{'='*60}")
    
    for i, vr in enumerate(result.get('validation_results', []), 1):
        status = "🔴" if vr.get('is_contradiction') else "🟢"
        print(f"\n{status} Проверка #{i}: {vr['law_reference']}")
        print(f"   Тип: {vr['contradiction_type']}")
        print(f"   Уверенность: {vr['confidence']:.0%}")
        print(f"   Серьезность: {vr.get('severity', 'n/a')}")
        print(f"   Пояснение: {vr['explanation'][:150]}...")
        if vr.get('quote_from_law'):
            print(f"   Цитата: \"{vr['quote_from_law'][:100]}...\"")
        if vr.get('suggestion'):
            print(f"   💡 Рекомендация: {vr['suggestion']}")


def create_test_change() -> dict:
    """Создает тестовое изменение."""
    return {
        "change_id": "test-vacation-001",
        "session_id": "test-session-001",
        "type": "modified",
        "element_number": "5.3",
        "old_text": "Работник имеет право на отпуск продолжительностью 24 календарных дня.",
        "new_text": "Работнику предоставляется отпуск продолжительностью 21 календарный день.",
        "full_chunk": "Статья 5. Права работника\n5.1. Право на ежегодный отпуск.\n5.2. Отпуск предоставляется по графику.\n5.3. Работнику предоставляется отпуск продолжительностью 21 календарный день.\n5.4. Отпуск может быть разделен на части.",
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


def create_test_change_no_contra() -> dict:
    """Создает тестовое изменение без противоречий."""
    return {
        "change_id": "test-schedule-001",
        "session_id": "test-session-001",
        "type": "added",
        "element_number": "5.5",
        "old_text": "",
        "new_text": "График отпусков утверждается нанимателем не позднее чем за две недели до начала календарного года.",
        "full_chunk": "Статья 5. Права работника\n...\n5.5. График отпусков утверждается нанимателем не позднее чем за две недели до начала календарного года.",
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


def main():
    parser = argparse.ArgumentParser(
        description='LLM Validator - проверка легальности изменений в документах',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  %(prog)s --test                    # Тестовый запуск
  %(prog)s --test --no-contra        # Тест без противоречий
  %(prog)s --file changes.json       # Проверка из файла
  %(prog)s --file changes.json --parallel  # Параллельная проверка
        """
    )
    
    parser.add_argument('--test', action='store_true', 
                       help='Тестовый режим с примером')
    parser.add_argument('--no-contra', action='store_true',
                       help='Использовать пример без противоречий (с --test)')
    parser.add_argument('--file', type=str,
                       help='JSON файл с изменениями для проверки')
    parser.add_argument('--parallel', action='store_true',
                       help='Использовать параллельную обработку')
    parser.add_argument('--api-key', type=str,
                       help='API ключ OpenRouter (или env DEEPSEEK_API_KEY)')
    parser.add_argument('--output', '-o', type=str,
                       help='Сохранить результат в файл')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Подробный вывод')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Определяем данные для проверки
    if args.test:
        if args.no_contra:
            changes = [create_test_change_no_contra()]
        else:
            changes = [create_test_change()]
    elif args.file:
        try:
            changes = load_changes_from_file(args.file)
            logger.info(f"Загружено {len(changes)} изменений из {args.file}")
        except Exception as e:
            logger.error(f"Ошибка загрузки файла: {e}")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(0)
    
    # Конфигурация
    try:
        config_kwargs = {}
        if args.api_key:
            config_kwargs['deepseek_api_key'] = args.api_key
        
        config = Config(**config_kwargs)
    except ValueError as e:
        logger.error(f"Ошибка конфигурации: {e}")
        logger.error("Установите DEEPSEEK_API_KEY или передайте --api-key")
        sys.exit(1)
    
    # Проверка
    try:
        with LLMValidator(config) as validator:
            results = []
            
            for i, change in enumerate(changes, 1):
                logger.info(f"Проверка {i}/{len(changes)}: {change.get('change_id')}")
                
                if args.parallel and len(change.get('relevant_laws', [])) > 1:
                    result = validator.validate_change_parallel(change)
                else:
                    result = validator.validate_change(change)
                
                results.append({
                    'change_id': result.change_id,
                    'validation_results': result.validation_results,
                    'overall_risk': result.overall_risk,
                    'overall_explanation': result.overall_explanation,
                    'total_laws_checked': result.total_laws_checked,
                    'contradictions_found': result.contradictions_found
                })
            
            # Вывод результатов
            for result in results:
                print_result(result)
            
            # Сохранение в файл
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                logger.info(f"Результаты сохранены в {args.output}")
            
            # Статистика
            stats = validator.get_stats()
            logger.info(f"Статистика: {stats['llm_stats']}")
            
    except Exception as e:
        logger.error(f"Ошибка проверки: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()