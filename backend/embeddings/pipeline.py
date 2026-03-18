import uuid
import logging
import psycopg2
from psycopg2.extras import execute_values
import numpy as np
from typing import List, Dict, Any, Tuple

from embeddings.chunker import LawDocumentChunker
from embeddings.embedder import E5Embedder

logger = logging.getLogger(__name__)

class AdminLawIngestionPipeline:
    """
    Пайплайн администратора: принимает документ, парсит статьи, делает чанки,
    создает векторы, сохраняет ВСЁ в БД с правильными UUID и возвращает (chunks, embeddings).
    """
    def __init__(self, db_config: Dict[str, str], chunk_size: int = 250):
        self.chunker = LawDocumentChunker(target_words=chunk_size)
        self.embedder = E5Embedder()
        self.db_config = db_config

    def run(self, document: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[np.ndarray]]:
        law_id = str(uuid.uuid4())
        law_ref = document.get("law_reference", "Неизвестный источник")

        articles_db_data = []
        chunks_info = []

        # 2. Обрабатываем статьи и чанки
        for article in document.get("articles", []):
            article_id = str(uuid.uuid4())
            art_number = article.get("number", "")

            articles_db_data.append({
                "id": article_id,
                "law_id": law_id,
                "article_number": art_number,
                "article_title": article.get("title", ""),
                "content": article.get("content", "")
            })

            # Чанкуем текст статьи
            text_chunks = self.chunker.chunk_article(article.get("content", ""))

            for i, text in enumerate(text_chunks):
                chunk_id = str(uuid.uuid4())

                orig_ref = f"{law_ref}, ст.{art_number}"
                if len(text_chunks) > 1:
                    orig_ref += f" (часть {i + 1})"

                chunks_info.append({
                    "chunk_id": chunk_id,
                    "article_id": article_id,
                    "text": text,
                    "original_reference": orig_ref
                })

        if not chunks_info:
            logger.warning("Документ не содержит текста для чанкинга.")
            return [], []

        logger.info(f"Генерация векторов для {len(chunks_info)} чанков...")
        texts_to_embed = [c["text"] for c in chunks_info]
        embeddings = self.embedder.embed(texts_to_embed)

        self._save_to_db(document, law_id, articles_db_data, chunks_info, embeddings)

        return chunks_info, embeddings

    def _save_to_db(self, doc: Dict, law_id: str, articles: List[Dict], chunks: List[Dict],
                    embeddings: List[np.ndarray]):
        """Сохраняет всю иерархию в PostgreSQL в рамках одной транзакции."""
        conn = psycopg2.connect(**self.db_config)
        conn.autocommit = False
        cursor = conn.cursor()

        try:
            logger.info("Сохранение в laws.catalog...")
            cursor.execute("""
                INSERT INTO laws.catalog (id, law_reference, law_name, hierarchy_level, source_url)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (law_reference) DO NOTHING
            """, (
                law_id, doc["law_reference"], doc["law_name"],
                doc.get("hierarchy_level", 1), doc.get("source_url", "")
            ))

            logger.info("Сохранение в laws.articles...")
            execute_values(cursor, """
                INSERT INTO laws.articles (id, law_id, article_number, article_title, content)
                VALUES %s
                ON CONFLICT (law_id, article_number) DO NOTHING
            """, [(a["id"], a["law_id"], a["article_number"], a["article_title"], a["content"]) for a in articles])

            logger.info("Сохранение в laws.chunks...")
            execute_values(cursor, """
                INSERT INTO laws.chunks (id, article_id, chunk_text, original_reference)
                VALUES %s
            """, [(c["chunk_id"], c["article_id"], c["text"], c["original_reference"]) for c in chunks])

            logger.info("Сохранение в laws.embeddings...")
            # Преобразуем векторы numpy в формат списка float, понятный для pgvector
            embeddings_data = []
            for chunk, emb in zip(chunks, embeddings):
                embed_id = str(uuid.uuid4())
                embeddings_data.append((embed_id, chunk["chunk_id"], emb.tolist(), self.embedder.model_name))

            execute_values(cursor, """
                INSERT INTO laws.embeddings (id, chunk_id, embedding, model_name)
                VALUES %s
            """, embeddings_data)

            conn.commit()
            logger.info("Закон успешно сохранен в базу данных!")

        except Exception as e:
            conn.rollback()
            logger.error(f"Ошибка БД во время сохранения: {e}")
            raise e
        finally:
            cursor.close()
            conn.close()