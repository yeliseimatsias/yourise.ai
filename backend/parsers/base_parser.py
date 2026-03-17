from abc import ABC, abstractmethod
import re

class BaseParser(ABC):
    """Абстрактный базовый класс для всех парсеров"""
    @abstractmethod
    def parse(self, file_path: str) -> dict:
        pass

    def detect_structure(self, text: str) -> list:
        lines = text.split('\n')
        elements = []
        current_element = None

        for line in lines:
            line = line.strip()
            if not line: continue

            element_type, number, title = self._identify_element(line)

            if element_type:
                if current_element:
                    current_element['content'] = current_element['content'].strip()
                    elements.append(current_element)

                # Теперь 'content' не пустой, а сразу получает текст заголовка (title)
                # Это уберет "Статья 23", но оставит всё, что было написано после неё
                current_element = {
                    'type': element_type,
                    'number': number,
                    'title': title,
                    'content': title if title else "",
                    'level': self._get_level(number),
                    'sequence': len(elements) + 1
                }
            else:
                if current_element:
                    # Добавляем последующие строки к контенту
                    sep = " " if current_element['content'] else ""
                    current_element['content'] += sep + line
                else:
                    # Текст в самом начале документа
                    elements.append({
                        'type': 'text',
                        'number': None,
                        'title': None,
                        'content': line,
                        'level': 0,
                        'sequence': len(elements) + 1
                    })

        if current_element:
            current_element['content'] = current_element['content'].strip()
            elements.append(current_element)
        return elements

    def _identify_element(self, line: str) -> tuple:
        article_match = re.search(r'^(?:\d+\.\s+)?(?:Статья|СТАТЬЯ)\s+(\d+[а-я]?)\.?\s*(.*)', line, re.IGNORECASE)
        if article_match:
            return ('article', article_match.group(1), article_match.group(2))

        chapter_match = re.search(r'^(?:Глава|ГЛАВА|Раздел|РАЗДЕл)\s+([IVXLCDM\d]+)\.?\s*(.*)', line, re.IGNORECASE)
        if chapter_match:
            return ('chapter', chapter_match.group(1), chapter_match.group(2))

        subclause_match = re.search(r'^(\d+\.\d+)\.?\s+(.*)', line)
        if subclause_match:
            return ('subclause', subclause_match.group(1), subclause_match.group(2))

        clause_match = re.search(r'^(\d+)\.\s+(.*)', line)
        if clause_match:
            return ('clause', clause_match.group(1), clause_match.group(2))

        return (None, None, None)

    def _get_level(self, number: str) -> int:
        if not number:
            return 1
        return number.count('.') + 1

    def clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        return text.strip()