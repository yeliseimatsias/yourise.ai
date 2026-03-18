"""
Парсер ответов от LLM.

Извлекает JSON из различных форматов ответов.
"""

import json
import re
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Структурированный результат валидации."""
    contradiction_type: str  # direct, indirect, none, unknown
    is_contradiction: bool
    confidence: float
    explanation: str
    quote_from_law: str
    suggestion: Optional[str]
    is_valid: bool = True  # Валиден ли сам результат (правильная структура)
    parse_error: Optional[str] = None


class ResponseParser:
    """Парсит ответы от DeepSeek и других LLM."""
    
    # Поля, которые обязательно должны быть в ответе
    REQUIRED_FIELDS = ['contradiction_type', 'is_contradiction', 'confidence', 'explanation']
    
    # Допустимые значения для contradiction_type
    VALID_TYPES = ['direct', 'indirect', 'none', 'unknown']
    
    @classmethod
    def parse(cls, response_text: str) -> ValidationResult:
        """
        Извлекает и валидирует JSON из ответа модели.
        
        Args:
            response_text: Сырой текст ответа от LLM
            
        Returns:
            ValidationResult с распарсенными данными
        """
        if not response_text or not response_text.strip():
            logger.error("Пустой ответ от модели")
            return cls._create_error_result("Пустой ответ от модели")
        
        # Пробуем различные стратегии парсинга
        parsed_data = None
        
        # Стратегия 1: Прямой парсинг всего текста как JSON
        try:
            parsed_data = json.loads(response_text.strip())
            logger.debug("Успешный прямой парсинг JSON")
        except json.JSONDecodeError:
            pass
        
        # Стратегия 2: Поиск JSON в markdown-блоках (```json ... ```)
        if parsed_data is None:
            parsed_data = cls._extract_from_markdown(response_text)
        
        # Стратегия 3: Поиск JSON-объекта в тексте
        if parsed_data is None:
            parsed_data = cls._extract_json_object(response_text)
        
        # Стратегия 4: Поиск JSON с исправлением распространенных ошибок
        if parsed_data is None:
            parsed_data = cls._extract_with_fixes(response_text)
        
        # Если ничего не сработало
        if parsed_data is None:
            logger.error(f"Не удалось распарсить ответ: {response_text[:200]}...")
            return cls._create_error_result("Не удалось распарсить JSON из ответа")
        
        # Валидируем структуру
        is_valid, error_msg = cls._validate_structure(parsed_data)
        if not is_valid:
            logger.warning(f"Невалидная структура ответа: {error_msg}")
            return cls._create_error_result(error_msg, partial_data=parsed_data)
        
        # Нормализуем и возвращаем результат
        return cls._normalize_result(parsed_data)
    
    @classmethod
    def _extract_from_markdown(cls, text: str) -> Optional[Dict]:
        """Извлекает JSON из markdown-блоков кода."""
        # Ищем блоки ```json ... ``` или ``` ... ```
        patterns = [
            r'```json\s*([\s\S]*?)\s*```',
            r'```\s*([\s\S]*?)\s*```'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    result = json.loads(match.strip())
                    logger.debug("Успешный парсинг из markdown-блока")
                    return result
                except json.JSONDecodeError:
                    continue
        
        return None
    
    @classmethod
    def _extract_json_object(cls, text: str) -> Optional[Dict]:
        """Ищет JSON-объект в тексте."""
        # Ищем объект между первой { и последней }
        try:
            start = text.index('{')
            end = text.rindex('}')
            if start < end:
                json_str = text[start:end+1]
                result = json.loads(json_str)
                logger.debug("Успешный парсинг JSON-объекта из текста")
                return result
        except (ValueError, json.JSONDecodeError):
            pass
        
        return None
    
    @classmethod
    def _extract_with_fixes(cls, text: str) -> Optional[Dict]:
        """Пытается исправить распространенные ошибки в JSON."""
        fixes = [
            # Убираем trailing commas
            (r',(\s*[}\]])', r'\1'),
            # Исправляем одинарные кавычки на двойные
            (r"'([^']*)'", r'"\1"'),
            # Убираем комментарии
            (r'//[^\n]*', ''),
        ]
        
        fixed_text = text
        for pattern, replacement in fixes:
            fixed_text = re.sub(pattern, replacement, fixed_text)
        
        try:
            result = json.loads(fixed_text)
            logger.debug("Успешный парсинг после исправлений")
            return result
        except json.JSONDecodeError:
            return None
    
    @classmethod
    def _validate_structure(cls, data: Dict) -> tuple[bool, str]:
        """Проверяет, что в ответе есть все обязательные поля."""
        if not isinstance(data, dict):
            return False, "Ответ не является объектом"
        
        # Проверяем обязательные поля
        for field in cls.REQUIRED_FIELDS:
            if field not in data:
                return False, f"Отсутствует обязательное поле: {field}"
        
        # Проверяем типы
        if data.get('contradiction_type') not in cls.VALID_TYPES:
            return False, f"Недопустимый contradiction_type: {data.get('contradiction_type')}"
        
        if not isinstance(data.get('is_contradiction'), bool):
            return False, "is_contradiction должен быть boolean"
        
        confidence = data.get('confidence')
        if not isinstance(confidence, (int, float)):
            return False, "confidence должен быть числом"
        if not (0 <= confidence <= 1):
            return False, "confidence должен быть между 0 и 1"
        
        return True, ""
    
    @classmethod
    def _normalize_result(cls, data: Dict) -> ValidationResult:
        """Нормализует и создает ValidationResult."""
        return ValidationResult(
            contradiction_type=data.get('contradiction_type', 'unknown'),
            is_contradiction=data.get('is_contradiction', False),
            confidence=float(data.get('confidence', 0)),
            explanation=data.get('explanation', ''),
            quote_from_law=data.get('quote_from_law', ''),
            suggestion=data.get('suggestion') if data.get('suggestion') else None,
            is_valid=True
        )
    
    @classmethod
    def _create_error_result(cls, error_msg: str, partial_data: Optional[Dict] = None) -> ValidationResult:
        """Создает результат с ошибкой парсинга."""
        return ValidationResult(
            contradiction_type='unknown',
            is_contradiction=False,
            confidence=0.0,
            explanation=f"Ошибка обработки ответа: {error_msg}",
            quote_from_law='',
            suggestion=None,
            is_valid=False,
            parse_error=error_msg
        )
    
    @classmethod
    def batch_parse(cls, responses: List[str]) -> List[ValidationResult]:
        """Парсит несколько ответов."""
        return [cls.parse(r) for r in responses]
