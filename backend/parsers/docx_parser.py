from docx import Document
from .base_parser import BaseParser
import re


class DOCXParser(BaseParser):
    """Парсер DOCX-документов"""
    def parse(self, file_path: str) -> dict:
        try:
            doc = Document(file_path)
        except Exception as e:
            print(f"Ошибка при открытии DOCX ({file_path}): {e}")
            return {
                'filename': file_path.split('/')[-1],
                'page_count': None,
                'word_count': 0,
                'elements': [],
                'metadata': {}
            }

        full_text = ""
        paragraphs_info = []

        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                full_text += text + "\n"
                paragraphs_info.append({
                    'text': text,
                    'style': para.style.name if para.style else 'Normal'
                })
        elements = self.detect_structure(full_text)
        has_structure = any(e.get('type') != 'text' for e in elements)
        if not has_structure:
            elements = self._extract_by_styles(paragraphs_info)

        word_count = len(full_text.split())

        metadata = {
            'author': doc.core_properties.author,
            'created': str(doc.core_properties.created) if doc.core_properties.created else None,
            'modified': str(doc.core_properties.modified) if doc.core_properties.modified else None
        }

        return {
            'filename': file_path.split('/')[-1],
            'page_count': None,
            'word_count': word_count,
            'elements': elements,
            'metadata': metadata
        }

    def _extract_by_styles(self, paragraphs_info: list) -> list:
        elements = []
        current_element = None
        sequence = 0

        for para in paragraphs_info:
            style = para['style'].lower() if para['style'] else ''
            text = para['text']

            if 'heading' in style or 'заголовок' in style:
                level_match = re.search(r'(\d+)', style)
                level = int(level_match.group(1)) if level_match else 1

                if current_element:
                    elements.append(current_element)

                sequence += 1
                current_element = {
                    'type': f'heading',
                    'number': None,
                    'title': text,
                    'content': text,
                    'level': level,
                    'sequence': sequence
                }
            else:
                if current_element and current_element.get('type') != 'text':
                    current_element['content'] += '\n' + text
                else:
                    sequence += 1
                    elements.append({
                        'type': 'text',
                        'number': None,
                        'title': None,
                        'content': text,
                        'level': 0,
                        'sequence': sequence
                    })

        if current_element:
            elements.append(current_element)

        return elements