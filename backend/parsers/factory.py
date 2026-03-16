class UnsupportedFormatError(Exception):
    """Возврат ошибки формата файла"""
    print(Exception)
class ParserFactory:
    """Фабрика для создания нужного парсера по расширению файла"""
    @staticmethod
    def get_parser(file_path: str):
        file_extension = file_path.lower().split('.')[-1]

        if file_extension == 'pdf':
            from .pdf_parser import PDFParser
            return PDFParser()
        elif file_extension in ['docx', 'doc']:
            from .docx_parser import DOCXParser
            return DOCXParser()
        else:
            raise UnsupportedFormatError(f"Формат .{file_extension} не поддерживается")