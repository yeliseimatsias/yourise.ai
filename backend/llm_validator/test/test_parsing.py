"""
Тесты для парсера ответов.
"""

import pytest
from llm_validator.response_parser.response_parser import ResponseParser, ValidationResult


class TestResponseParser:
    """Тесты парсера ответов."""
    
    def test_parse_valid_json(self):
        """Тест парсинга валидного JSON."""
        response = '''{"contradiction_type": "direct", "is_contradiction": true, "confidence": 0.95, "explanation": "Тест", "quote_from_law": "Статья 1", "suggestion": "Исправить"}'''
        
        result = ResponseParser.parse(response)
        
        assert result.is_valid
        assert result.contradiction_type == "direct"
        assert result.is_contradiction is True
        assert result.confidence == 0.95
        assert result.explanation == "Тест"
        assert result.quote_from_law == "Статья 1"
        assert result.suggestion == "Исправить"
    
    def test_parse_json_in_markdown(self):
        """Тест парсинга JSON в markdown-блоке."""
        response = '''```json
{
    "contradiction_type": "indirect",
    "is_contradiction": true,
    "confidence": 0.75,
    "explanation": "Косвенное противоречие",
    "quote_from_law": "Цитата",
    "suggestion": null
}
```'''
        
        result = ResponseParser.parse(response)
        
        assert result.is_valid
        assert result.contradiction_type == "indirect"
        assert result.confidence == 0.75
    
    def test_parse_json_with_text(self):
        """Тест парсинга JSON окруженного текстом."""
        response = '''Вот результат анализа:

{
    "contradiction_type": "none",
    "is_contradiction": false,
    "confidence": 0.92,
    "explanation": "Нет противоречия",
    "quote_from_law": "",
    "suggestion": null
}

Надеюсь, это поможет!'''
        
        result = ResponseParser.parse(response)
        
        assert result.is_valid
        assert result.contradiction_type == "none"
        assert result.is_contradiction is False
    
    def test_parse_empty_response(self):
        """Тест обработки пустого ответа."""
        result = ResponseParser.parse("")
        
        assert not result.is_valid
        assert result.parse_error is not None
    
    def test_parse_invalid_json(self):
        """Тест обработки невалидного JSON."""
        result = ResponseParser.parse("это не json")
        
        assert not result.is_valid
        assert result.parse_error is not None
    
    def test_parse_missing_fields(self):
        """Тест обработки JSON с отсутствующими полями."""
        response = '{"contradiction_type": "direct", "confidence": 0.5}'
        
        result = ResponseParser.parse(response)
        
        assert not result.is_valid
    
    def test_parse_invalid_types(self):
        """Тест обработки JSON с неверными типами."""
        response = '{"contradiction_type": "invalid", "is_contradiction": "yes", "confidence": 0.5, "explanation": "test"}'
        
        result = ResponseParser.parse(response)
        
        assert not result.is_valid
    
    def test_parse_confidence_out_of_range(self):
        """Тест обработки confidence вне диапазона."""
        response = '{"contradiction_type": "direct", "is_contradiction": true, "confidence": 1.5, "explanation": "test"}'
        
        result = ResponseParser.parse(response)
        
        assert not result.is_valid
    
    def test_parse_single_quotes(self):
        """Тест парсинга JSON с одинарными кавычками."""
        response = "{'contradiction_type': 'none', 'is_contradiction': false, 'confidence': 0.8, 'explanation': 'test'}"
        
        result = ResponseParser.parse(response)
        
        assert result.is_valid
        assert result.contradiction_type == "none"
    
    def test_parse_trailing_comma(self):
        """Тест парсинга JSON с trailing comma."""
        response = '{"contradiction_type": "none", "is_contradiction": false, "confidence": 0.8, "explanation": "test",}'
        
        result = ResponseParser.parse(response)
        
        assert result.is_valid


class TestValidationResult:
    """Тесты структуры ValidationResult."""
    
    def test_create_valid_result(self):
        """Тест создания валидного результата."""
        result = ValidationResult(
            contradiction_type="direct",
            is_contradiction=True,
            confidence=0.95,
            explanation="Прямое противоречие",
            quote_from_law="Статья 1",
            suggestion="Исправить",
            is_valid=True
        )
        
        assert result.is_valid
        assert result.confidence == 0.95
    
    def test_create_error_result(self):
        """Тест создания результата с ошибкой."""
        result = ValidationResult(
            contradiction_type="unknown",
            is_contradiction=False,
            confidence=0.0,
            explanation="Ошибка",
            quote_from_law="",
            suggestion=None,
            is_valid=False,
            parse_error="Не удалось распарсить"
        )
        
        assert not result.is_valid
        assert result.parse_error == "Не удалось распарсить"