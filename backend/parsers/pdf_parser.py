import pdfplumber
from .base_parser import BaseParser

class PDFParser(BaseParser):
    """Парсер PDF-документов"""
    def parse(self, file_path: str) -> dict:
        extraction = self._extract_text(file_path)
        elements = self.detect_structure(extraction['text'])
        word_count = len(extraction['text'].split())

        return {
            'filename': file_path.split('/')[-1],
            'page_count': extraction['page_count'],
            'word_count': word_count,
            'elements': elements,
            'metadata': extraction['metadata']
        }

    def _extract_text(self, file_path: str) -> dict:
        result = {'text': '', 'page_count': 0, 'metadata': {}}

        try:
            with pdfplumber.open(file_path) as pdf:
                result['page_count'] = len(pdf.pages)
                result['metadata'] = pdf.metadata or {}

                for page in pdf.pages:
                    page_text = page.extract_text() or ''
                    if page_text:
                        result['text'] += f"{page_text}\n"
        except Exception as e:
            print(f"Ошибка при парсинге PDF ({file_path}): {e}")

        return result