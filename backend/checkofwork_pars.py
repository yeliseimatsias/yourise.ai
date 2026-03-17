import os
os.environ['HF_HOME'] = 'D:/huggingface_cache'

from embandding import DocumentProcessingPipeline

# Ваш исходный словарь
data = {
    "filename": "trudovoy_kodeks_2026.docx",
    "elements": [
        {
            "type": "article",
            "number": "5",
            "title": "Права и обязанности работника",
            "content": "Работник имеет право на ежегодный оплачиваемый отпуск...",
        },
        {
            "type": "clause",
            "number": "5.1",
            "title": None,
            "content": "Отпуск предоставляется продолжительностью 24 календарных дня",
        }
    ]
}


def main():
    pipeline = DocumentProcessingPipeline(chunk_size=250)
    chunks, embeddings = pipeline.run(data)

    # Результат, готовый к отправке в БД
    print(f"Создано чанков: {len(chunks)}")
    print(f"Создано векторов: {len(embeddings)}")

    if chunks:
        print("\nПример первого чанка:")
        print(chunks[0]['text'])
        print(f"Размерность вектора: {embeddings[0].shape}")  # Ожидаем (1024,)
        print(f"Тип данных вектора: {type(embeddings[0])}")  # Ожидаем <class 'numpy.ndarray'>


if __name__ == "__main__":
    main()