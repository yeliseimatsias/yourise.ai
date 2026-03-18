import re
from typing import List, Dict, Any

class DocumentChunker:
    """
    Класс для разбиения структурированного словаря документа на текстовые чанки.
    Поддерживает размер чанков в заданных пределах (по умолчанию ~250 слов).
    """
    def __init__(self, target_words: int = 250):
        self.target_words = target_words

    def process(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        filename = document.get("filename", "unknown_document")
        elements = document.get("elements", [])

        chunks = []
        current_article_context = ""
        current_chunk_words = []

        for el in elements:
            if el.get("type") == "article":
                number = el.get("number", "")
                title = el.get("title")
                title_str = f" {title}" if title else ""
                current_article_context = f"Статья {number}.{title_str}"

            content = el.get("content", "")
            if not content:
                continue

            words = content.split()
            idx = 0

            while idx < len(words):
                if not current_chunk_words:
                    context_header = f"[{filename} | {current_article_context}]"
                    current_chunk_words.extend(context_header.split())

                space_left = self.target_words - len(current_chunk_words)

                slice_words = words[idx: idx + space_left]
                current_chunk_words.extend(slice_words)
                idx += len(slice_words)

                if len(current_chunk_words) >= self.target_words:
                    chunks.append({
                        "context": current_article_context,
                        "text": " ".join(current_chunk_words)
                    })
                    current_chunk_words = []

        if current_chunk_words:
            chunks.append({
                "context": current_article_context,
                "text": " ".join(current_chunk_words)
            })

        return chunks