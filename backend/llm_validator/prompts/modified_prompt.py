"""
Промпт для проверки измененного текста.
"""

from .base_prompt import BasePrompt


class ModifiedPrompt(BasePrompt):
    """Промпт для проверки измененного текста."""
    
    @classmethod
    def build(cls, change_data: dict, law_data: dict) -> str:
        """
        Строит промпт для проверки изменения.
        
        Args:
            change_data: Данные об изменении (old_text, new_text, full_chunk)
            law_data: Данные о законе (law_reference, chunk_text)
            
        Returns:
            Полный текст промпта
        """
        change_type_str = cls.format_change_type('modified')
        
        prompt = f"""{cls.SYSTEM_MESSAGE}

{cls.get_few_shot_examples()}

=== КОНТЕКСТ ПРОВЕРКИ ===
Тип изменения: {change_type_str}
Номер элемента: {change_data.get('element_number', 'не указан')}

ИЗМЕНЕНИЕ:
- Было: {change_data.get('old_text', '[не указано]')}
- Стало: {change_data['new_text']}

Полный контекст (весь пункт целиком):
{change_data['full_chunk']}

=== СТАТЬЯ ЗАКОНА ДЛЯ СРАВНЕНИЯ ===
Источник: {law_data['law_reference']}
Уровень иерархии: {law_data.get('hierarchy_level', 'не указан')}
Релевантность: {law_data.get('similarity', 0):.0%}

Текст статьи:
{law_data['chunk_text']}

=== ЗАДАНИЕ ===
Проанализируй, соответствует ли НОВАЯ редакция (то, что стало) требованиям данной статьи закона.

КРИТЕРИИ ПРОВЕРКИ:
1. Числовые значения: сравни цифры в тексте и законе
2. Модальность: проверь глаголы (обязан/вправе/может/должен)
3. Субъекты: кто должен действовать, кто имеет право
4. Условия: при каких обстоятельствах применяется норма
5. Последствия: не ухудшает ли изменение положение сторон

ВАЖНО: Сравни именно НОВУЮ редакцию с законом, а не разницу между старой и новой!

Ответь строго в формате JSON без markdown-разметки."""
        
        return prompt
