import re
import difflib
from typing import Dict, Any, Tuple, List

def tokenize(text: str) -> set:
    """Разбивает текст на слова (токены) в нижнем регистре для Jaccard."""
    if not text:
        return set()
    return set(re.findall(r'\b\w+\b', text.lower()))


def jaccard_similarity(text1: str, text2: str) -> float:
    """Вычисляет Jaccard similarity (пересечение / объединение токенов)."""
    set1, set2 = tokenize(text1), tokenize(text2)
    if not set1 and not set2:
        return 1.0
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union > 0 else 0.0

def sequence_similarity(text1: str, text2: str) -> float:
    """Вычисляет схожесть последовательностей с помощью SequenceMatcher."""
    if not text1 and not text2:
        return 1.0
    return difflib.SequenceMatcher(None, text1, text2).ratio()

def context_similarity(el1: Dict[str, Any], el2: Dict[str, Any]) -> float:
    """Сравнивает контекст: тип элемента, уровень и заголовок."""
    score = 0.0
    if el1.get("type") == el2.get("type"):
        score += 0.4
    if el1.get("level") == el2.get("level"):
        score += 0.2

    title1, title2 = el1.get("title") or "", el2.get("title") or ""
    score += 0.4 * sequence_similarity(title1, title2)
    return score

def combined_similarity(el1: Dict[str, Any], el2: Dict[str, Any]) -> float:
    """
    Комбинированная оценка (по ТЗ):
    - 40% Jaccard
    - 40% SequenceMatcher
    - 20% Контекст
    """
    t1, t2 = el1.get("content", ""), el2.get("content", "")
    j_sim = jaccard_similarity(t1, t2)
    s_sim = sequence_similarity(t1, t2)
    c_sim = context_similarity(el1, el2)

    return (0.4 * j_sim) + (0.4 * s_sim) + (0.2 * c_sim)

def get_word_diff(old_text: str, new_text: str) -> Dict[str, List[str]]:
    """Находит добавленные и удаленные слова."""
    old_words = old_text.split() if old_text else []
    new_words = new_text.split() if new_text else []

    diff = difflib.ndiff(old_words, new_words)
    added, removed = [], []

    for token in diff:
        if token.startswith('+ '):
            added.append(token[2:])
        elif token.startswith('- '):
            removed.append(token[2:])

    return {"added_words": added, "removed_words": removed}