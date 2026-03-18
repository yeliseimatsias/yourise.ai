import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer

class E5Embedder:
    """
    Класс для создания эмбеддингов E5.
    """
    def __init__(self, model_name: str = 'intfloat/multilingual-e5-large', batch_size: int = 32):
        self.model_name = model_name
        self.batch_size = batch_size
        self.model = SentenceTransformer(self.model_name)

    def embed(self, texts: List[str]) -> List[np.ndarray]:
        """
        Генерирует векторы. Для E5 эталонные документы (в базе) 
        должны иметь префикс 'passage: '.
        """
        prefixed_texts = [f"passage: {text}" for text in texts]
        embeddings = self.model.encode(
            prefixed_texts,
            batch_size=self.batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        return list(embeddings)