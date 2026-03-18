# import os
# os.environ['HF_HOME'] = 'D:/huggingface_cache'
# from llm_validator import LLMValidatorPipeline
#
#
# def main():
#     print("🚀 Инициализация пайплайна LLM Validator...")
#     # При инициализации класс автоматически подтянет ключи из .env файла
#     # и загрузит модель эмбеддингов E5 (это может занять пару секунд)
#     try:
#         pipeline = LLMValidatorPipeline()
#     except Exception as e:
#         print(f"❌ Ошибка инициализации (проверьте .env и БД): {e}")
#         return
#
#     # Подготавливаем данные об изменении, которые пришли от пользователя/фронтенда.
#     # Обратите внимание: change_id должен существовать в таблице core.changes вашей БД,
#     # так как пайплайн попытается сохранить результаты проверки с привязкой к этому ID.
#     input_data = {
#         "change_id": "550e8400-e29b-41d4-a716-446655440000",
#         "session_id": "660e8400-e29b-41d4-a716-446655441111",
#         "type": "modified",
#         "element_number": "5.3",
#         "old_text": "Работник имеет право на отпуск продолжительностью 24 календарных дня.",
#         "new_text": "Работнику предоставляется отпуск продолжительностью 21 календарный день.",
#         "full_chunk": "Статья 5. Права работника\n5.1. Право на ежегодный отпуск.\n5.2. Отпуск предоставляется по графику.\n5.3. Работнику предоставляется отпуск продолжительностью 21 календарный день.\n5.4. Отпуск может быть разделен на части.",
#         "document_type": "local_act",
#         "document_level": 7
#     }
#
#     print("\n🔍 Запуск векторного поиска и проверки через DeepSeek...")
#
#     try:
#         # Вызываем наш метод, который возвращает готовую JSON-строку
#         json_response = pipeline.process_change_to_json(input_data)
#
#         # 1. Выводим результат в консоль
#         print("\n=== РЕЗУЛЬТАТ ВАЛИДАЦИИ (JSON) ===")
#         print(json_response)
#
#         # 2. Сохраняем результат в файл (например, для истории или дебага)
#         output_filename = f"result_{input_data['change_id']}.json"
#         with open(output_filename, "w", encoding="utf-8") as f:
#             f.write(json_response)
#
#         print(f"\n✅ Результат успешно сохранен в файл: {output_filename}")
#
#     except Exception as e:
#         print(f"\n❌ Произошла ошибка во время обработки: {e}")
#
#
# if __name__ == "__main__":
#     main()


import json
from llm_validator.report import ReportGenerator  # Импортируем наш класс из файла report.py


def main():
    print("🚀 Подготовка данных для отчета...")

    # 1. Информация о сессии (обычно берется из вашей таблицы core.sessions)
    session_info = {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "old_document": "Трудовой_договор_2025.docx",
        "new_document": "Трудовой_договор_2026.docx"
    }

    # 2. Массив изменений (Это результат работы вашей LLM-модели, склеенный с исходным текстом)
    changes_data = [
        {
            # --- Данные из базы (то, что прислал фронтенд) ---
            "change_id": "c1111111-e29b-41d4-a716-446655440001",
            "element_number": "5.3",
            "change_type": "modified",
            "old_text": "Работник имеет право на отпуск 24 дня.",
            "new_text": "Работнику предоставляется отпуск 21 день.",

            # --- Данные от LLM (результат работы core.py) ---
            "overall_risk": "red",
            "overall_explanation": "Найдено 1 критических нарушений.",
            "validation_results": [
                {
                    "law_reference": "Трудовой кодекс РБ, ст. 155",
                    "law_text": "Основной отпуск предоставляется продолжительностью не менее 24 календарных дней.",
                    "contradiction_type": "direct",
                    "is_contradiction": True,
                    "confidence": 0.95,
                    "explanation": "Сокращение отпуска с 24 до 21 дня напрямую нарушает ТК РБ.",
                    "quote_from_law": "не менее 24 календарных дней",
                    "suggestion": "Восстановить минимальную продолжительность отпуска до 24 дней.",
                    "severity": "high"
                }
            ]
        },
        {
            # --- Второе изменение (Зеленое, без нарушений) ---
            "change_id": "c2222222-e29b-41d4-a716-446655440002",
            "element_number": "6.1",
            "change_type": "added",
            "old_text": "",
            "new_text": "Работодатель обязуется предоставлять бесплатный чай и кофе в офисе.",

            "overall_risk": "green",
            "overall_explanation": "Изменение соответствует законодательству.",
            "validation_results": []  # Пусто, так как нарушений нет
        }
    ]

    print("📊 Инициализация генератора отчетов...")
    generator = ReportGenerator(session_info, changes_data)

    # --- ШАГ 1: ГЕНЕРАЦИЯ JSON ДЛЯ ФРОНТЕНДА ---
    json_report = generator.generate_json_report()

    # Сохраняем JSON в файл (или отправляем по API)
    json_filename = f"report_{session_info['id']}.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(json_report, f, ensure_ascii=False, indent=2)
    print(f"✅ Создан JSON-отчет: {json_filename}")

    # --- ШАГ 2: ГЕНЕРАЦИЯ DOCX ДЛЯ ЮРИСТОВ ---
    docx_stream = generator.generate_docx_report()

    # Сохраняем поток байтов в реальный файл Word
    docx_filename = f"report_{session_info['id']}.docx"
    with open(docx_filename, "wb") as f:
        f.write(docx_stream.read())
    print(f"✅ Создан DOCX-отчет: {docx_filename}")

    print("\n🎉 Все отчеты успешно сгенерированы! Проверьте папку проекта.")


if __name__ == "__main__":
    main()