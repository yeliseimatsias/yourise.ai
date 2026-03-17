import uuid
from typing import Dict, Any, List, Tuple
from .metrics import combined_similarity, get_word_diff


class DocumentDiffer:
    def __init__(self, match_threshold: float = 0.8, possible_match_threshold: float = 0.5):
        self.match_threshold = match_threshold
        self.possible_match_threshold = possible_match_threshold

    def compare(self, old_doc: Dict[str, Any], new_doc: Dict[str, Any]) -> Dict[str, Any]:
        session_id = str(uuid.uuid4())

        old_elements = old_doc.get("elements", [])
        new_elements = new_doc.get("elements", [])

        # Шаг 1: Построение матрицы схожести
        matches = self._find_best_matches(old_elements, new_elements)

        # Шаг 2-3: Кластеризация и определение типов изменений
        changes, summary = self._build_changes(old_elements, new_elements, matches)

        return {
            "session_id": session_id,
            "old_document": old_doc.get("filename"),
            "new_document": new_doc.get("filename"),
            "summary": summary,
            "changes": changes
        }

    def _find_best_matches(self, old_elements: List[Dict], new_elements: List[Dict]) -> Dict:
        """Жадный алгоритм поиска лучших совпадений (similarity > 50%)."""
        similarities = []
        for i, old_el in enumerate(old_elements):
            for j, new_el in enumerate(new_elements):
                sim = combined_similarity(old_el, new_el)
                if sim >= self.possible_match_threshold:
                    similarities.append((sim, i, j))

        # Сортируем от самых похожих к наименее похожим
        similarities.sort(key=lambda x: x[0], reverse=True)

        matched_old = set()
        matched_new = set()
        best_matches = {}

        for sim, i, j in similarities:
            if i not in matched_old and j not in matched_new:
                best_matches[i] = (j, sim)
                matched_old.add(i)
                matched_new.add(j)

        return best_matches

    def _build_changes(self, old_elements: List[Dict], new_elements: List[Dict], matches: Dict) -> Tuple[List, Dict]:
        changes = []
        summary = {"total_changes": 0, "added": 0, "deleted": 0, "modified": 0, "moved": 0}

        matched_new_indices = set()

        # Анализ существующих и удаленных элементов
        for i, old_el in enumerate(old_elements):
            old_num = old_el.get("number")

            if i in matches:
                j, sim = matches[i]
                new_el = new_elements[j]
                new_num = new_el.get("number")
                matched_new_indices.add(j)

                is_same_num = (old_num == new_num)
                is_exact_match = (sim > 0.99)  # Учитываем погрешность float

                if is_same_num and is_exact_match:
                    continue  # Без изменений

                change_type = ""
                needs_validation = True

                if is_same_num and not is_exact_match:
                    change_type = "modified"
                    summary["modified"] += 1
                elif not is_same_num and is_exact_match:
                    change_type = "moved"
                    needs_validation = False  # Перемещение без изменения текста
                    summary["moved"] += 1
                elif not is_same_num and not is_exact_match:
                    change_type = "moved_and_modified"
                    summary["moved"] += 1
                    summary["modified"] += 1

                diff = get_word_diff(old_el.get("content", ""), new_el.get("content", ""))
                search_text = new_el.get("content", "")

                change_obj = self._format_change_obj(
                    c_type=change_type, old_el=old_el, new_el=new_el, sim=sim,
                    diff=diff, needs_validation=needs_validation, search_text=search_text
                )
                changes.append(change_obj)
            else:
                # Нет пары -> Удалено
                summary["deleted"] += 1
                change_obj = {
                    "type": "deleted",
                    "element_number": old_num,
                    "old_element": old_el,
                    "needs_validation": True,
                    "search_text": old_el.get("content", ""),
                    "search_data": self._build_search_data("deleted", old_el.get("content"), old_num)
                }
                changes.append(change_obj)

        # Анализ добавленных (тех new_elements, которые не попали в matches)
        for j, new_el in enumerate(new_elements):
            if j not in matched_new_indices:
                summary["added"] += 1
                new_num = new_el.get("number")
                change_obj = {
                    "type": "added",
                    "element_number": new_num,
                    "new_element": new_el,
                    "needs_validation": True,
                    "search_text": new_el.get("content", ""),
                    "search_data": self._build_search_data("added", new_el.get("content"), new_num)
                }
                changes.append(change_obj)

        summary["total_changes"] = sum(summary.values()) - summary["total_changes"]  # Пересчет общего кол-ва
        return changes, summary

    def _format_change_obj(self, c_type, old_el, new_el, sim, diff, needs_validation, search_text):
        """Вспомогательный метод для сборки объекта изменения."""
        obj = {
            "type": c_type,
            "similarity": round(sim, 4),
            "needs_validation": needs_validation
        }

        if c_type in ("moved", "moved_and_modified"):
            obj["old_number"] = old_el.get("number")
            obj["new_number"] = new_el.get("number")
        else:
            obj["element_number"] = old_el.get("number")

        if c_type != "moved":
            obj["diff"] = diff
            obj["search_text"] = search_text

            # Подготовка данных для эмбеддингов
            elem_num = new_el.get("number") if new_el.get("number") else old_el.get("number")
            obj["search_data"] = self._build_search_data(c_type, search_text, elem_num)

        # Если перемещен без изменений, сохраняем единый element
        if c_type == "moved":
            obj["element"] = new_el
        else:
            obj["old_element"] = old_el
            obj["new_element"] = new_el

        return obj

    def _build_search_data(self, c_type: str, text: str, element_number: str) -> Dict[str, Any]:
        """Формирует блок для отправки в модуль эмбеддингов."""
        return {
            "change_id": str(uuid.uuid4()),
            "type": c_type,
            "search_text": text,
            "full_chunk": text,
            "element_number": element_number,
            "needs_validation": True
        }