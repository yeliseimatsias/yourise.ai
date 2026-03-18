from .schemas import ChangeInput, LawData

class PromptBuilder:
    SYSTEM_MESSAGE = """Ты — эксперт по законодательству Республики Беларусь.
Твоя задача — анализировать изменения в документах и определять их соответствие законам.
Отвечай СТРОГО в формате JSON без markdown-разметки:
{
    "contradiction_type": "direct" | "indirect" | "none",
    "is_contradiction": true | false,
    "confidence": 0.0-1.0,
    "explanation": "почему",
    "quote_from_law": "цитата",
    "suggestion": "как исправить",
    "severity": "high" | "medium" | "low"
}"""

    @classmethod
    def build(cls, change: ChangeInput, law: LawData) -> str:
        # Формируем контекст в зависимости от типа
        if change.type == "added":
            change_context = f"ДОБАВЛЕННЫЙ ТЕКСТ:\n{change.new_text}"
        elif change.type == "deleted":
            change_context = f"УДАЛЕННЫЙ ТЕКСТ:\n{change.old_text}"
        else: # modified
            change_context = f"ИЗМЕНЕНИЕ:\n- Было: {change.old_text}\n- Стало: {change.new_text}"

        prompt = f"""{cls.SYSTEM_MESSAGE}

=== КОНТЕКСТ ПРОВЕРКИ ===
Тип изменения: {change.type}
Номер элемента: {change.element_number}

{change_context}

Полный контекст элемента:
{change.full_chunk}

=== СТАТЬЯ ЗАКОНА ДЛЯ СРАВНЕНИЯ ===
Источник: {law.law_reference}
Текст статьи:
{law.chunk_text}

Проанализируй соответствие текста требованиям данной статьи закона и верни JSON."""
        return prompt