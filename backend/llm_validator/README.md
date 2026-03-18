# LLM Validator

Модуль для проверки юридической легальности изменений в документах с использованием DeepSeek R1.

## Возможности

- ✅ Проверка изменений на соответствие законодательству РБ
- ✅ Поддержка различных типов изменений (added, deleted, modified)
- ✅ Определение типа противоречия (direct, indirect, none)
- ✅ Оценка уверенности (confidence score)
- ✅ Агрегация рисков по нескольким законам
- ✅ Сохранение результатов в PostgreSQL или SQLite
- ✅ Параллельная обработка для скорости
- ✅ Повторные попытки при ошибках API

## Установка

```bash
# Клонирование репозитория
git clone https://github.com/yourise/llm-validator.git
cd llm-validator

# Установка
pip install -e .

# Или с поддержкой PostgreSQL
pip install -e ".[postgres]"
```

## Быстрый старт

```python
from llm_validator import LLMValidator, Config

# Конфигурация (можно передать напрямую)
config = Config(deepseek_api_key="your-api-key")

# Или через переменные окружения
# export DEEPSEEK_API_KEY="your-api-key"
# config = Config()

# Создаем валидатор
validator = LLMValidator(config)

# Данные для проверки
change_data = {
    "change_id": "550e8400-e29b-41d4-a716-446655440000",
    "session_id": "660e8400-e29b-41d4-a716-446655441111",
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

# Проверяем
result = validator.validate_change(change_data)

print(f"Риск: {result.overall_risk}")
print(f"Пояснение: {result.overall_explanation}")
print(f"Противоречий: {result.contradictions_found}/{result.total_laws_checked}")

# Детали
for vr in result.validation_results:
    print(f"\nЗакон: {vr['law_reference']}")
    print(f"Тип: {vr['contradiction_type']}")
    print(f"Уверенность: {vr['confidence']}")
    print(f"Пояснение: {vr['explanation']}")
    if vr['suggestion']:
        print(f"Рекомендация: {vr['suggestion']}")

# Закрываем соединения
validator.close()
```

## Конфигурация

### Способы задания конфигурации

**1. Через конструктор (приоритетный):**
```python
config = Config(
    deepseek_api_key="sk-or-v1-...",
    deepseek_model="deepseek/deepseek-r1",
    llm_temperature=0.1,
    llm_retries=3
)
```

**2. Через переменные окружения:**
```bash
export DEEPSEEK_API_KEY="sk-or-v1-..."
export DEEPSEEK_MODEL="deepseek/deepseek-r1"
export DB_HOST="localhost"
export DB_NAME="yourise"
```

**3. Значения по умолчанию:**
```python
config = Config()  # Использует значения по умолчанию + env
```

### Параметры конфигурации

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `deepseek_api_key` | API ключ OpenRouter | - |
| `deepseek_base_url` | URL API | https://openrouter.ai/api/v1 |
| `deepseek_model` | Модель LLM | deepseek/deepseek-r1 |
| `llm_temperature` | Температура генерации | 0.1 |
| `llm_max_tokens` | Макс. токенов в ответе | 2000 |
| `llm_retries` | Попыток при ошибке | 3 |
| `db_config` | Конфиг БД | SQLite in-memory |

## API DeepSeek

Модуль использует DeepSeek R1 через OpenRouter API (бесплатно):

1. Получите API ключ: https://openrouter.ai/keys
2. Установите в `DEEPSEEK_API_KEY` или передайте в Config

## Типы изменений

- `added` - добавлен новый текст
- `deleted` - текст удален
- `modified` - текст изменен
- `moved_and_modified` - текст перемещен и изменен

## Типы противоречий

- `direct` - прямое противоречие (текст нарушает закон)
- `indirect` - косвенное противоречие (создает риски)
- `none` - нет противоречия
- `unknown` - не удалось определить

## Уровни риска

- `red` - высокий риск (прямые противоречия)
- `yellow` - средний риск (потенциальные проблемы)
- `green` - низкий риск (нет противоречий)

## Пакетная обработка

```python
changes = [change1, change2, change3, ...]

# С колбэком прогресса
def on_progress(current, total):
    print(f"{current}/{total}")

results = validator.validate_batch(changes, progress_callback=on_progress)

# Статистика
for r in results:
    print(f"{r.change_id}: {r.overall_risk}")
```

## Параллельная обработка

```python
# Для одного изменения с несколькими законами
result = validator.validate_change_parallel(change_data, max_workers=5)
```

## Работа с БД

```python
from llm_validator.db import ValidatorRepository

# PostgreSQL
repo = ValidatorRepository({
    'host': 'localhost',
    'port': '5432',
    'dbname': 'yourise',
    'user': 'postgres',
    'password': 'secret'
})

# Или SQLite (in-memory для тестов)
repo = ValidatorRepository({'dbname': ':memory:'})

# Получить историю проверок
validations = repo.get_validations_by_change(change_id)

# Получить риск
risk = repo.get_change_risk(change_id)

# Статистика сессии
stats = repo.get_session_stats(session_id)
print(f"Red: {stats['red']}, Yellow: {stats['yellow']}, Green: {stats['green']}")

repo.close()
```

## Тестирование

```bash
# Установка зависимостей для разработки
pip install -e ".[dev]"

# Запуск тестов
pytest tests/

# С покрытием
pytest --cov=llm_validator tests/
```

## Структура пакета

```
llm_validator/
├── __init__.py           # Экспорты пакета
├── config.py             # Конфигурация
├── main.py               # Главный класс LLMValidator
├── clients/
│   ├── __init__.py
│   └── deepseek_client.py   # Клиент для DeepSeek API
├── prompts/
│   ├── __init__.py
│   ├── base_prompt.py       # Базовый промпт
│   ├── added_prompt.py      # Промпт для добавлений
│   ├── modified_prompt.py   # Промпт для изменений
│   └── deleted_prompt.py    # Промпт для удалений
├── parsers/
│   ├── __init__.py
│   └── response_parser.py   # Парсинг ответов LLM
├── aggregators/
│   ├── __init__.py
│   └── risk_aggregator.py   # Агрегация рисков
└── db/
    ├── __init__.py
    └── validator_repository.py  # Работа с БД
```

## Лицензия

MIT License
