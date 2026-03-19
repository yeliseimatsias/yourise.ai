import os
import logging
from typing import Dict, Any
import json
os.environ['HF_HOME'] = 'D:/huggingface_cache'
import uuid
import psycopg2

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
def admin_ingest_law(file_path: str, db_config: dict) -> bool:
    """
    Принимает файл, извлекает метаданные из его содержимого и сохраняет в БД.
    """
    logger.info(f"Начало обработки документа: {file_path}")

    try:
        # 1. Получаем парсер и сырые данные
        parser = ParserFactory.get_parser(file_path)
        parsed_data = parser.parse(file_path)
        elements = parsed_data.get('elements', [])

        if not elements:
            logger.error("Парсер не нашел данных в файле.")
            return False

        # --- БЛОК АВТОМАТИЧЕСКОГО ИЗВЛЕЧЕНИЯ МЕТАДАННЫХ ---

        # 2. Ищем заголовок (law_name)
        # Проверяем первые 10 элементов: ищем строку в ВЕРХНЕМ РЕГИСТРЕ (как на скрине)
        law_name = "Неизвестный документ"
        for el in elements[:10]:
            content = el.get('content', '').strip()
            # Условие: длинный текст капсом или содержит ключевое слово 'РЕШЕНИЕ'
            if len(content) > 20 and (content.isupper() or "РЕШЕНИЕ" in content.upper()):
                law_name = content
                break

        # 3. Создаем law_reference (уникальный ключ для БД)
        # Берем либо имя файла, либо первые 50 символов названия
        law_ref = parsed_data.get('filename', 'ref_id').split('.')[0]

        # 4. Определяем уровень иерархии (по умолчанию 1)
        hierarchy_level = 1
        # -------------------------------------------------

        # 5. Собираем статьи (фильтруем только 'article' и 'clause' со скринов)
        articles_for_db = []
        for el in elements:
            if el.get('type') not in ['article', 'clause']:
                continue

            articles_for_db.append({
                "number": el.get('number') or "б/н",
                "title": el.get('title') or (el.get('content', '')[:100] + "..."),
                "content": el.get('content', '')
            })

        # Формируем итоговый объект
        document_to_ingest = {
            "law_reference": law_ref,
            "law_name": law_name,
            "hierarchy_level": hierarchy_level,
            "source_url": "",  # Если ссылки нет в JSON, оставляем пустой
            "articles": articles_for_db
        }

        # 6. Прогоняем через пайплайн
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

     # ✅ СОЗДАЁМ СЕССИЮ В БД
    try:
        with psycopg2.connect(**config.db_config) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO core.sessions (id, status, progress, changes_total, changes_processed)
                    VALUES (%s, 'processing', 0, 0, 0)
                    ON CONFLICT (id) DO NOTHING
                    RETURNING id
                """, (session_id,))
                saved = cur.fetchone()
                if saved:
                    logger.info(f"✅ Сессия {saved[0]} создана")
                else:
                    logger.warning(f"⚠️ Сессия {session_id} уже существовала")
                conn.commit()
    except Exception as e:
        logger.error(f"❌ Не удалось создать сессию: {e}")
        return {"error": str(e)}
    
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

                # Сохраняем change в БД
                with psycopg2.connect(**config.db_config) as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            INSERT INTO core.changes 
                            (id, session_id, element_number, change_type, old_text, new_text, processing_status)
                            VALUES (%s, %s, %s, %s, %s, %s, 'pending')
                            ON CONFLICT (id) DO NOTHING
                        """, (
                            llm_payload["change_id"],
                            session_id,
                            llm_payload["element_number"],
                            llm_payload["type"],
                            llm_payload["old_text"],
                            llm_payload["new_text"]
                        ))
                        conn.commit()

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
        with open(f'report_{session_id}.json', 'w', encoding = 'utf-8') as f:
            json.dump(final_json, f, ensure_ascii=False, indent = 4)

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

def test_load_law():
    """Тестовая загрузка закона"""
    file_path = r"C:\Users\Lenovo\Downloads\H11300016_1357765200.pdf"
    
    logger.info("🚀 Начинаем загрузку закона...")
    
    result = admin_ingest_law(
        file_path=file_path,
        db_config=config.db_config
    )
    
    if result:
        logger.info("✅ Закон успешно загружен!")
        
        # Проверяем, сколько статей загрузилось
        with psycopg2.connect(**config.db_config) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM laws.articles")
                articles_count = cur.fetchone()[0]
                logger.info(f"📊 Статей в БД: {articles_count}")
    else:
        logger.error("❌ Ошибка загрузки закона")


if __name__ == "__main__":
    user_process_comparison(old_file=r"C:\Users\Lenovo\Downloads\old_test.docx", new_file=r"C:\Users\Lenovo\Downloads\new_test.docx")
    # test_load_law()