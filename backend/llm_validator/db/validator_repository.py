"""
Репозиторий для сохранения результатов валидации.
Только PostgreSQL!
"""

import logging
from typing import Dict, Optional, List, Any
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class ValidatorRepository:
    """Репозиторий для работы с результатами валидации (только PostgreSQL)."""

    def __init__(self, db_config: Dict[str, str]):
        """
        Инициализирует подключение к PostgreSQL.

        Args:
            db_config: Конфигурация БД (host, port, dbname, user, password)
        """
        self.db_config = db_config
        self.conn = None
        self._connect()
    
    def _connect(self):
        """Устанавливает соединение с PostgreSQL."""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.conn.autocommit = False
            logger.info("PostgreSQL подключен")
        except Exception as e:
            logger.error(f"Ошибка подключения к PostgreSQL: {e}")
            raise
    
    def save_validation(
        self,
        change_id: str,
        law_reference: str,
        law_text: str,
        explanation: str,
        confidence: float
    ) -> int:
        """
        Сохраняет результат валидации в таблицу core.validation_results.
        """
        try:
            cursor = self.conn.cursor()

            cursor.execute("""
                INSERT INTO core.validation_results
                (change_id, law_reference, law_text, explanation, confidence)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (change_id, law_reference, law_text, explanation, confidence))

            self.conn.commit()
            result_id = cursor.fetchone()[0]
            cursor.close()

            logger.debug(f"Сохранен результат валидации: id={result_id}")
            return result_id

        except Exception as e:
            self.conn.rollback()
            logger.error(f"Ошибка сохранения валидации: {e}")
            raise
    
    def close(self):
        """Закрывает соединение с БД."""
        if self.conn:
            self.conn.close()
            logger.info("Соединение с БД закрыто")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()