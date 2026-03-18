"""
Репозиторий для сохранения результатов валидации.

Поддерживает PostgreSQL и SQLite (для тестирования).
"""

import logging
from typing import Dict, Optional, List, Any
from datetime import datetime
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Пробуем импортировать psycopg2, если недоступен - используем sqlite
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    import sqlite3


# class ValidatorRepository:
#     """Репозиторий для работы с результатами валидации."""
#
#     def __init__(self, db_config: Dict[str, str]):
#         """
#         Инициализирует репозиторий.
#
#         Args:
#             db_config: Конфигурация БД (host, port, dbname, user, password)
#                       или {'dbname': ':memory:'} для SQLite
#         """
#         self.db_config = db_config
#         self.is_sqlite = db_config.get('dbname') == ':memory:' or not POSTGRES_AVAILABLE
#
        # if self.is_sqlite:
        #     self._init_sqlite()
        # else:
        #     self._init_postgres()
    
    # def _init_sqlite(self):
    #     """Инициализирует SQLite (в памяти или файл)."""
    #     db_name = self.db_config.get('dbname', ':memory:')
    #     self.conn = sqlite3.connect(db_name, check_same_thread=False)
    #     self.conn.row_factory = sqlite3.Row
    #     self._create_tables_sqlite()
    #     logger.info(f"SQLite инициализирован: {db_name}")
    
    # def _init_postgres(self):
    #     """Инициализирует подключение к PostgreSQL."""
    #     if not POSTGRES_AVAILABLE:
    #         raise RuntimeError("psycopg2 не установлен. Установите: pip install psycopg2-binary")
    #
    #     try:
    #         self.conn = psycopg2.connect(**self.db_config)
    #         self.conn.autocommit = False
    #         self._create_tables_postgres()
    #         logger.info("PostgreSQL подключен")
    #     except Exception as e:
    #         logger.error(f"Ошибка подключения к PostgreSQL: {e}")
    #         raise
    
    # def _create_tables_sqlite(self):
    #     """Создает таблицы в SQLite."""
    #     cursor = self.conn.cursor()
    #
    #     # Таблица результатов валидации
    #     cursor.execute("""
    #         CREATE TABLE IF NOT EXISTS validation_results (
    #             id INTEGER PRIMARY KEY AUTOINCREMENT,
    #             change_id TEXT NOT NULL,
    #             law_reference TEXT NOT NULL,
    #             law_text TEXT,
    #             contradiction_type TEXT,
    #             is_contradiction BOOLEAN,
    #             confidence REAL,
    #             explanation TEXT,
    #             quote_from_law TEXT,
    #             suggestion TEXT,
    #             severity TEXT,
    #             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    #         )
    #     """)
    #
    #     # Таблица для отслеживания рисков изменений
    #     cursor.execute("""
    #         CREATE TABLE IF NOT EXISTS change_risks (
    #             change_id TEXT PRIMARY KEY,
    #             session_id TEXT,
    #             overall_risk TEXT,
    #             explanation TEXT,
    #             updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    #         )
    #     """)
    #
    #     self.conn.commit()
    #
    # def _create_tables_postgres(self):
    #     """Создает таблицы в PostgreSQL."""
    #     cursor = self.conn.cursor()
    #
    #     cursor.execute("""
    #         CREATE TABLE IF NOT EXISTS validation_results (
    #             id SERIAL PRIMARY KEY,
    #             change_id UUID NOT NULL,
    #             law_reference TEXT NOT NULL,
    #             law_text TEXT,
    #             contradiction_type VARCHAR(20),
    #             is_contradiction BOOLEAN,
    #             confidence FLOAT,
    #             explanation TEXT,
    #             quote_from_law TEXT,
    #             suggestion TEXT,
    #             severity VARCHAR(10),
    #             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    #         )
    #     """)
    #
    #     cursor.execute("""
    #         CREATE TABLE IF NOT EXISTS change_risks (
    #             change_id UUID PRIMARY KEY,
    #             session_id UUID,
    #             overall_risk VARCHAR(10),
    #             explanation TEXT,
    #             updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    #         )
    #     """)
    #
    #     self.conn.commit()
    #     cursor.close()
    
    # def save_validation(
    #     self,
    #     change_id: str,
    #     law_reference: str,
    #     law_text: str,
    #     contradiction_type: str,
    #     explanation: str,
    #     confidence: float,
    #     is_contradiction: Optional[bool] = None,
    #     quote_from_law: str = "",
    #     suggestion: Optional[str] = None,
    #     severity: str = "low"
    # ) -> int:
    #     """
    #     Сохраняет результат валидации.
    #
    #     Returns:
    #         ID сохраненной записи
    #     """
    #     if is_contradiction is None:
    #         is_contradiction = contradiction_type in ['direct', 'indirect']
    #
    #     try:
    #         cursor = self.conn.cursor()
    #
    #         if self.is_sqlite:
    #             cursor.execute("""
    #                 INSERT INTO validation_results
    #                 (change_id, law_reference, law_text, contradiction_type,
    #                  is_contradiction, confidence, explanation, quote_from_law,
    #                  suggestion, severity)
    #                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    #             """, (change_id, law_reference, law_text, contradiction_type,
    #                   is_contradiction, confidence, explanation, quote_from_law,
    #                   suggestion, severity))
    #         else:
    #             cursor.execute("""
    #                 INSERT INTO validation_results
    #                 (change_id, law_reference, law_text, contradiction_type,
    #                  is_contradiction, confidence, explanation, quote_from_law,
    #                  suggestion, severity)
    #                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    #                 RETURNING id
    #             """, (change_id, law_reference, law_text, contradiction_type,
    #                   is_contradiction, confidence, explanation, quote_from_law,
    #                   suggestion, severity))
    #
    #         self.conn.commit()
    #         result_id = cursor.lastrowid if self.is_sqlite else cursor.fetchone()[0]
    #         cursor.close()
    #
    #         logger.debug(f"Сохранен результат валидации: id={result_id}")
    #         return result_id
    #
    #     except Exception as e:
    #         self.conn.rollback()
    #         logger.error(f"Ошибка сохранения валидации: {e}")
    #         raise
    #
    # def update_change_risk(
    #     self,
    #     change_id: str,
    #     overall_risk: str,
    #     session_id: Optional[str] = None,
    #     explanation: str = ""
    # ):
    #     """Обновляет общий риск для изменения."""
    #     try:
    #         cursor = self.conn.cursor()
    #
    #         if self.is_sqlite:
    #             cursor.execute("""
    #                 INSERT OR REPLACE INTO change_risks
    #                 (change_id, session_id, overall_risk, explanation, updated_at)
    #                 VALUES (?, ?, ?, ?, ?)
    #             """, (change_id, session_id, overall_risk, explanation, datetime.now()))
    #         else:
    #             cursor.execute("""
    #                 INSERT INTO change_risks
    #                 (change_id, session_id, overall_risk, explanation, updated_at)
    #                 VALUES (%s, %s, %s, %s, %s)
    #                 ON CONFLICT (change_id)
    #                 DO UPDATE SET
    #                     overall_risk = EXCLUDED.overall_risk,
    #                     explanation = EXCLUDED.explanation,
    #                     updated_at = EXCLUDED.updated_at
    #             """, (change_id, session_id, overall_risk, explanation, datetime.now()))
    #
    #         self.conn.commit()
    #         cursor.close()
    #
    #         logger.debug(f"Обновлен риск для {change_id}: {overall_risk}")
    #
    #     except Exception as e:
    #         self.conn.rollback()
    #         logger.error(f"Ошибка обновления риска: {e}")
    #         raise
    #
    # def get_validations_by_change(self, change_id: str) -> List[Dict[str, Any]]:
    #     """Получает все валидации для конкретного изменения."""
    #     cursor = self.conn.cursor()
    #
    #     if self.is_sqlite:
    #         cursor.execute("""
    #             SELECT * FROM validation_results
    #             WHERE change_id = ?
    #             ORDER BY created_at DESC
    #         """, (change_id,))
    #     else:
    #         cursor.execute("""
    #             SELECT * FROM validation_results
    #             WHERE change_id = %s
    #             ORDER BY created_at DESC
    #         """, (change_id,))
    #
    #     rows = cursor.fetchall()
    #     cursor.close()
    #
    #     return [dict(row) for row in rows]
    #
    # def get_change_risk(self, change_id: str) -> Optional[Dict[str, Any]]:
    #     """Получает риск для конкретного изменения."""
    #     cursor = self.conn.cursor()
    #
    #     if self.is_sqlite:
    #         cursor.execute("""
    #             SELECT * FROM change_risks WHERE change_id = ?
    #         """, (change_id,))
    #     else:
    #         cursor.execute("""
    #             SELECT * FROM change_risks WHERE change_id = %s
    #         """, (change_id,))
    #
    #     row = cursor.fetchone()
    #     cursor.close()
    #
    #     return dict(row) if row else None
    #
    # def get_session_stats(self, session_id: str) -> Dict[str, Any]:
    #     """Получает статистику по сессии."""
    #     cursor = self.conn.cursor()
    #
    #     if self.is_sqlite:
    #         cursor.execute("""
    #             SELECT
    #                 overall_risk,
    #                 COUNT(*) as count
    #             FROM change_risks
    #             WHERE session_id = ?
    #             GROUP BY overall_risk
    #         """, (session_id,))
    #     else:
    #         cursor.execute("""
    #             SELECT
    #                 overall_risk,
    #                 COUNT(*) as count
    #             FROM change_risks
    #             WHERE session_id = %s
    #             GROUP BY overall_risk
    #         """, (session_id,))
    #
    #     rows = cursor.fetchall()
    #     cursor.close()
    #
    #     stats = {"red": 0, "yellow": 0, "green": 0, "total": 0}
    #     for row in rows:
    #         stats[row[0]] = row[1]
    #         stats["total"] += row[1]
    #
    #     return stats
    #
    # def close(self):
    #     """Закрывает соединение с БД."""
    #     if hasattr(self, 'conn') and self.conn:
    #         self.conn.close()
    #         logger.info("Соединение с БД закрыто")
    #
    # def __enter__(self):
    #     return self
    #
    # def __exit__(self, exc_type, exc_val, exc_tb):
    #     self.close()
