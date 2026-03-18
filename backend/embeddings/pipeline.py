from typing import Dict, Any, List, Tuple
import numpy as np
from .chunker import DocumentChunker
from .embedder import E5Embedder

class DocumentProcessingPipeline:
    """
    Пайплайн, принимающий словарь, делающий чанки и возвращающий
    список чанков и список соответствующих им векторов numpy.
    """
    def __init__(self, chunk_size: int = 250):
        self.chunker = DocumentChunker(target_words=chunk_size)
        self.embedder = E5Embedder()

    def run(self, document: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[np.ndarray]]:
        """
        Основной метод.
        Возвращает:
        1. Список словарей-чанков (каждый содержит сам текст и метаданные/контекст)
        2. Список эмбеддингов (numpy arrays размерности 1024)
        """
        chunks = self.chunker.process(document)
        if not chunks:
            return [], []

        texts_to_embed = [chunk["text"] for chunk in chunks]
        embeddings = self.embedder.embed(texts_to_embed)

        return chunks, embeddings