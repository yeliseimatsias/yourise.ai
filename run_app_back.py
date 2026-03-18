import os
import logging
from typing import Dict, Any
import json
os.environ['HF_HOME'] = 'D:/huggingface_cache'
import uuid

# Импорты модулей парсинга
from backend.parsers.factory import ParserFactory, UnsupportedFormatError

# Импорты модулей эмбеддинга и БД (админский пайплайн)
from backend.embeddings.pipeline import AdminLawIngestionPipeline

# Импорт генератора отчетов
from backend.llm_validator.report import ReportGenerator
from backend.llm_validator.config import Config
from backend.llm_validator.core import LLMValidatorPipeline
from backend.semantic_differ.analyzer import DocumentDiffer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

config = Config()

# ==============================================================================
# ФУНКЦИЯ 1: ПАЙПЛАЙН АДМИНИСТРАТОРА (Загрузка эталонов в БД)
# ==============================================================================
def admin_ingest_law(file_path: str, db_config: dict, law_metadata: dict) -> bool:
    """
    Принимает файл (PDF/DOCX), парсит его, разбивает на чанки, генерирует векторы
    через E5 и сохраняет в эталонную базу данных (схема laws).

    :param file_path: Путь к файлу закона (например, 'documents/tk_rf.docx')
    :param db_config: Словарь с настройками подключения к PostgreSQL
    :param law_metadata: Данные о законе (law_reference, law_name, hierarchy_level)
    """
    logger.info(f"Начало обработки эталонного документа: {file_path}")

    try:
        # 1. Получаем нужный парсер (PDF или DOCX) из Фабрики
        parser = ParserFactory.get_parser(file_path)

        # 2. Парсим документ (вытаскиваем структуру, статьи, текст)
        parsed_data = parser.parse(file_path)
        logger.info(f"Документ успешно распарсен. Найдено элементов: {len(parsed_data['elements'])}")

        # 3. Адаптируем распарсенные элементы под формат, который ждет AdminLawIngestionPipeline
        articles_for_db = []
        for index, el in enumerate(parsed_data['elements']):
            # Если парсер не нашел номер статьи, даем ей порядковый номер
            art_number = el.get('number') or str(index + 1)

            articles_for_db.append({
                "number": art_number,
                "title": el.get('title') or el.get('type', 'Раздел'),
                "content": el.get('content', '')
            })

        # Формируем итоговый словарь документа
        document_to_ingest = {
            "law_reference": law_metadata.get("law_reference", parsed_data['filename']),
            "law_name": law_metadata.get("law_name", "Без названия"),
            "hierarchy_level": law_metadata.get("hierarchy_level", 1),
            "source_url": law_metadata.get("source_url", ""),
            "articles": articles_for_db
        }

        # 4. Прогоняем через пайплайн эмбеддингов и БД
        # ВАЖНО: Убедитесь, что в pipeline.py строка `self._save_to_db(...)` раскомментирована!
        pipeline = AdminLawIngestionPipeline(db_config=db_config)
        chunks, embeddings = pipeline.run(document_to_ingest)

        logger.info(f"Успех! Документ сохранен в базу. Чанков: {len(chunks)}")
        return True

    except UnsupportedFormatError as e:
        logger.error(f"Ошибка формата файла: {e}")
        return False
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при загрузке закона: {e}")
        return False


def user_process_comparison(old_file: str, new_file: str) -> Dict[str, Any]:
    """
    Сравнивает два файла, проверяет изменения через DeepSeek LLM
    и выдает JSON для фронтенда + путь к созданному DOCX.
    """
    logger.info(f"--- ПОЛЬЗОВАТЕЛЬ: Сравнение {old_file} и {new_file} ---")
    session_id = str(uuid.uuid4())

    try:
        # 1. Парсинг файлов
        old_doc = ParserFactory.get_parser(old_file).parse(old_file)
        new_doc = ParserFactory.get_parser(new_file).parse(new_file)

        # 2. Семантический анализ изменений
        differ = DocumentDiffer(match_threshold=0.8)
        diff_results = differ.compare(old_doc, new_doc)

        # 3. Инициализация LLM-валидатора
        llm_pipeline = LLMValidatorPipeline(config=config)

        validated_changes = []
        for change in diff_results.get("changes", []):
            # Проверяем только то, что изменилось или добавилось
            if change['type'] in ['modified', 'added', 'moved_and_modified']:

                # Подготовка входных данных для LLM (Schema: ChangeInput)
                llm_payload = {
                    "change_id": str(uuid.uuid4()),
                    "session_id": session_id,
                    "type": change['type'],
                    "element_number": change.get('element_number') or change.get('new_number') or "—",
                    "old_text": change.get('old_element', {}).get('content', ""),
                    "new_text": change.get('new_element', {}).get('content', ""),
                    "full_chunk": change.get('new_element', {}).get('content', ""),
                    "document_type": "contract",
                    "document_level": 1
                }

                # Запрос к DeepSeek (Поиск в БД -> Промпт -> Ответ)
                val_res_str = llm_pipeline.process_change_to_json(llm_payload)
                val_res = json.loads(val_res_str)

                # Собираем данные для генератора отчета
                validated_changes.append({
                    **llm_payload,
                    "overall_risk": val_res.get("overall_risk", "green"),
                    "overall_explanation": val_res.get("overall_explanation", ""),
                    "validation_results": val_res.get("validation_results", [])
                })
            else:
                # Для удаленных или перемещенных без изменений — просто добавляем в список
                validated_changes.append({
                    "change_type": change['type'],
                    "old_text": change.get('old_element', {}).get('content', ""),
                    "new_text": change.get('new_element', {}).get('content', ""),
                    "overall_risk": "green"
                })

        # 4. Генерация отчетов
        session_info = {
            "id": session_id,
            "old_document": old_file,
            "new_document": new_file
        }

        report_gen = ReportGenerator(session_info, validated_changes)

        # Финальный JSON для UI
        final_json = report_gen.generate_json_report()

        # Финальный DOCX файл
        docx_data = report_gen.generate_docx_report()
        docx_path = f"report_{session_id}.docx"
        with open(docx_path, "wb") as f:
            f.write(docx_data.read())

        final_json["docx_report_path"] = docx_path
        logger.info(f"✅ Обработка завершена. Файл отчета: {docx_path}")

        return final_json

    except Exception as e:
        logger.error(f"❌ Ошибка пользовательского пайплайна: {e}")
        return {"error": str(e)}