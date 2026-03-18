from typing import List


class LawDocumentChunker:
    """
    Чанкер, адаптированный под структуру законов.
    Бьет текст СТРОГО внутри одной статьи, чтобы сохранить реляционную связь в БД.
    """
    def __init__(self, target_words: int = 250):
        self.target_words = target_words

    def chunk_article(self, content: str) -> List[str]:
        """Разбивает текст одной статьи на куски заданного размера."""
        if not content:
            return []

        words = content.split()
        chunks = []

        for i in range(0, len(words), self.target_words):
            chunk_text = " ".join(words[i: i + self.target_words])
            chunks.append(chunk_text)

        return chunks