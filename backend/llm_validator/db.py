import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class ValidatorRepository:
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.use_mock = False

        # Пытаемся подключиться. Если базы нет — включаем режим заглушки.
        try:
            # Просто тестовое подключение, чтобы проверить доступность
            conn = psycopg2.connect(**self.db_config)
            conn.close()
        except Exception as e:
            logger.warning(f"⚠️ БД недоступна. Включаем MOCK-режим (заглушки) для тестирования LLM!")
            self.use_mock = True

    def _get_connection(self):
        return psycopg2.connect(**self.db_config)

    def search_similar_laws(self, embedding: List[float], limit: int = 3) -> List[Dict[str, Any]]:
        """Ищет релевантные статьи в БД или отдает заглушку."""
        if self.use_mock:
            logger.info("[MOCK] Отдаем тестовый закон про 24 дня отпуска вместо поиска по БД.")
            return [{
                "law_reference": "Трудовой кодекс РБ, ст. 155 (MOCK)",
                "chunk_text": "Основной отпуск предоставляется продолжительностью не менее 24 календарных дней.",
                "hierarchy_level": 1,
                "similarity": 0.99
            }]

        # Реальный поиск в БД (если она есть)
        vector_str = '[' + ','.join(map(str, embedding)) + ']'
        query = """
            SELECT 
                c.original_reference as law_reference,
                c.chunk_text,
                cat.hierarchy_level,
                1 - (e.embedding <=> %s::vector) as similarity
            FROM laws.embeddings e
            JOIN laws.chunks c ON e.chunk_id = c.id
            JOIN laws.articles a ON c.article_id = a.id
            JOIN laws.catalog cat ON a.law_id = cat.id
            ORDER BY e.embedding <=> %s::vector
            LIMIT %s;
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (vector_str, vector_str, limit))
                return [dict(row) for row in cur.fetchall()]

    def save_validation_result(self, change_id: str, result: dict):
        """Сохраняет результаты в БД или игнорирует в Mock-режиме."""
        if self.use_mock:
            logger.info(f"[MOCK] Имитация сохранения результата для {change_id}")
            return

        # Реальное сохранение (если БД есть)
        query = """
            INSERT INTO core.validation_results 
            (change_id, law_reference, law_text, explanation, confidence)
            VALUES (%s, %s, %s, %s, %s);
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    change_id,
                    result['law_reference'],
                    result['law_text'],
                    result['explanation'],
                    result['confidence']
                ))
            conn.commit()