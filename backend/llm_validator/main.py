"""
Главный модуль LLM Validator.

Предоставляет API для проверки легальности изменений в документах.
"""

import json
import logging
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from .config import Config
from .clients.deepseek_client import DeepSeekClient
from .prompts.modified_prompt import ModifiedPrompt
from .prompts.added_prompt import AddedPrompt
from .prompts.deleted_prompt import DeletedPrompt
from .parsers.response_parser import ResponseParser, ValidationResult
from .aggregators.risk_aggregator import RiskAggregator, AggregatedRisk
# from .db.validator_repository import ValidatorRepository

logger = logging.getLogger(__name__)


@dataclass
class ValidationOutput:
    """Структурированный выход валидации."""
    change_id: str
    validation_results: List[Dict[str, Any]]
    overall_risk: str
    overall_explanation: str
    total_laws_checked: int
    contradictions_found: int


class LLMValidator:
    """
    Главный класс для проверки легальности изменений.
    
    Args:
        config: Конфигурация (Config или dict)
        db_config: Опциональная конфигурация БД (переопределяет config.db_config)
    """
    
    def __init__(
        self, 
        config: Optional[Config] = None,
        db_config: Optional[Dict[str, str]] = None
    ):
        self.config = config or Config()
        self.config.validate()  # Проверяем, что API ключ задан
        
        # Инициализируем клиент DeepSeek
        self.client = DeepSeekClient(
            api_key=self.config.deepseek_api_key,
            base_url=self.config.deepseek_base_url,
            model=self.config.deepseek_model,
            timeout=self.config.request_timeout
        )
        
        # Инициализируем БД
        db_cfg = db_config or self.config.db_config
        # self.db = ValidatorRepository(db_cfg)
        
        # Парсер и агрегатор
        self.parser = ResponseParser()
        self.aggregator = RiskAggregator()
        
        # Кэш промптов
        self._prompt_builders = {
            'modified': ModifiedPrompt,
            'added': AddedPrompt,
            'deleted': DeletedPrompt,
            'moved_and_modified': ModifiedPrompt  # Используем тот же промпт
        }
    
    def validate_change(self, change_data: Dict[str, Any]) -> ValidationOutput:
        """
        Проверяет одно изменение против всех релевантных законов.
        
        Args:
            change_data: Данные об изменении с релевантными законами
            
        Returns:
            ValidationOutput с результатами проверки
        """
        change_id = change_data.get('change_id', 'unknown')
        logger.info(f"Начало проверки изменения {change_id}")
        
        all_results = []
        relevant_laws = change_data.get('relevant_laws', [])
        
        if not relevant_laws:
            logger.warning(f"Нет релевантных законов для проверки {change_id}")
            return ValidationOutput(
                change_id=change_id,
                validation_results=[],
                overall_risk="green",
                overall_explanation="Нет релевантных законов для проверки",
                total_laws_checked=0,
                contradictions_found=0
            )
        
        # Последовательная проверка по каждому закону
        for law in relevant_laws:
            result = self._validate_against_law(change_data, law)
            if result:
                all_results.append(result)
        
        # Агрегируем результаты
        aggregated = self.aggregator.aggregate(all_results)
        
        # Сохраняем общий риск в БД
        # self.db.update_change_risk(
        #     change_id=change_id,
        #     overall_risk=aggregated.overall_risk,
        #     session_id=change_data.get('session_id'),
        #     explanation=aggregated.overall_explanation
        # )
        
        logger.info(f"Проверка {change_id} завершена: риск={aggregated.overall_risk}, "
                   f"противоречий={aggregated.contradictions_found}/{aggregated.total_checks}")
        
        return ValidationOutput(
            change_id=change_id,
            validation_results=all_results,
            overall_risk=aggregated.overall_risk,
            overall_explanation=aggregated.overall_explanation,
            total_laws_checked=aggregated.total_checks,
            contradictions_found=aggregated.contradictions_found
        )
    
    def validate_change_parallel(
        self, 
        change_data: Dict[str, Any],
        max_workers: Optional[int] = None
    ) -> ValidationOutput:
        """
        Проверяет изменение параллельно (для нескольких законов).
        
        Args:
            change_data: Данные об изменении
            max_workers: Максимальное количество параллельных запросов
            
        Returns:
            ValidationOutput с результатами
        """
        change_id = change_data.get('change_id', 'unknown')
        relevant_laws = change_data.get('relevant_laws', [])
        
        if not relevant_laws:
            return self.validate_change(change_data)  # Делегируем обычному методу
        
        max_workers = max_workers or self.config.max_concurrent_requests
        max_workers = min(max_workers, len(relevant_laws))
        
        logger.info(f"Параллельная проверка {change_id} с {max_workers} workers")
        
        all_results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_law = {
                executor.submit(self._validate_against_law, change_data, law): law 
                for law in relevant_laws
            }
            
            for future in as_completed(future_to_law):
                law = future_to_law[future]
                try:
                    result = future.result()
                    if result:
                        all_results.append(result)
                except Exception as e:
                    logger.error(f"Ошибка проверки по закону {law.get('law_reference')}: {e}")
        
        # Агрегируем и сохраняем
        aggregated = self.aggregator.aggregate(all_results)
        
        # self.db.update_change_risk(
        #     change_id=change_id,
        #     overall_risk=aggregated.overall_risk,
        #     session_id=change_data.get('session_id'),
        #     explanation=aggregated.overall_explanation
        # )
        
        return ValidationOutput(
            change_id=change_id,
            validation_results=all_results,
            overall_risk=aggregated.overall_risk,
            overall_explanation=aggregated.overall_explanation,
            total_laws_checked=aggregated.total_checks,
            contradictions_found=aggregated.contradictions_found
        )
    
    def _validate_against_law(
        self, 
        change_data: Dict[str, Any], 
        law: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Проверяет изменение против одного закона.
        
        Args:
            change_data: Данные об изменении
            law: Данные о законе
            
        Returns:
            Результат проверки или None при ошибке
        """
        law_ref = law.get('law_reference', 'unknown')
        logger.debug(f"  Проверка по закону: {law_ref}")
        
        # Выбираем подходящий промпт
        change_type = change_data.get('type', 'modified')
        prompt_builder = self._prompt_builders.get(change_type, ModifiedPrompt)
        
        try:
            prompt = prompt_builder.build(change_data, law)
        except Exception as e:
            logger.error(f"  ❌ Ошибка построения промпта: {e}")
            return None
        
        # Отправляем запрос к DeepSeek
        response = self.client.generate_with_retry(
            prompt,
            max_retries=self.config.llm_retries,
            temperature=self.config.llm_temperature,
            max_tokens=self.config.llm_max_tokens
        )
        
        if not response.success:
            logger.error(f"  ❌ Ошибка API: {response.error}")
            return None
        
        # Парсим ответ
        parsed = self.parser.parse(response.content)
        
        if not parsed.is_valid:
            logger.warning(f"  ⚠️ Невалидный ответ: {parsed.parse_error}")
            # Возвращаем частичный результат с пометкой об ошибке
            return {
                'law_reference': law_ref,
                'law_text': law.get('chunk_text', ''),
                'contradiction_type': 'unknown',
                'is_contradiction': False,
                'confidence': 0.0,
                'explanation': f"Ошибка обработки: {parsed.parse_error}",
                'quote_from_law': '',
                'suggestion': None,
                'severity': 'low',
                'parse_error': True
            }
        
        # Определяем серьезность
        severity = self.aggregator.calculate_severity({
            'contradiction_type': parsed.contradiction_type,
            'is_contradiction': parsed.is_contradiction,
            'confidence': parsed.confidence
        })
        
        # Формируем результат
        result = {
            'law_reference': law_ref,
            'law_text': law.get('chunk_text', ''),
            'contradiction_type': parsed.contradiction_type,
            'is_contradiction': parsed.is_contradiction,
            'confidence': parsed.confidence,
            'explanation': parsed.explanation,
            'quote_from_law': parsed.quote_from_law,
            'suggestion': parsed.suggestion,
            'severity': severity,
            'tokens_used': response.tokens_used
        }
        
        # Сохраняем в БД
        try:
            self.db.save_validation(
                change_id=change_data['change_id'],
                law_reference=law_ref,
                law_text=law.get('chunk_text', ''),
                contradiction_type=parsed.contradiction_type,
                is_contradiction=parsed.is_contradiction,
                confidence=parsed.confidence,
                explanation=parsed.explanation,
                quote_from_law=parsed.quote_from_law,
                suggestion=parsed.suggestion,
                severity=severity
            )
        except Exception as e:
            logger.warning(f"  ⚠️ Ошибка сохранения в БД: {e}")
        
        # Логируем результат
        status = "🔴" if parsed.is_contradiction else "🟢"
        logger.info(f"  {status} {law_ref}: {parsed.contradiction_type} "
                   f"(conf: {parsed.confidence:.2f}, sev: {severity})")
        
        return result
    
    def validate_batch(
        self, 
        changes: List[Dict[str, Any]],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[ValidationOutput]:
        """
        Проверяет несколько изменений.
        
        Args:
            changes: Список изменений для проверки
            progress_callback: Функция обратного вызова (current, total)
            
        Returns:
            Список результатов
        """
        results = []
        total = len(changes)
        
        logger.info(f"Начало пакетной проверки: {total} изменений")
        
        for i, change in enumerate(changes, 1):
            result = self.validate_change(change)
            results.append(result)
            
            if progress_callback:
                progress_callback(i, total)
            
            if i % 10 == 0:
                logger.info(f"Прогресс: {i}/{total} ({i/total*100:.1f}%)")
        
        logger.info(f"Пакетная проверка завершена: {total} изменений")
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Возвращает статистику работы валидатора."""
        return {
            'llm_stats': self.client.get_stats(),
            'config': {
                'model': self.config.deepseek_model,
                'temperature': self.config.llm_temperature,
                'max_tokens': self.config.llm_max_tokens
            }
        }
    
    def close(self):
        """Закрывает соединения и освобождает ресурсы."""
        self.db.close()
        logger.info("Валидатор закрыт")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def validate_single_change(
    change_data: Dict[str, Any],
    api_key: str,
    **config_kwargs
) -> Dict[str, Any]:
    """
    Упрощенная функция для одноразовой проверки.
    
    Args:
        change_data: Данные об изменении
        api_key: API ключ DeepSeek/OpenRouter
        **config_kwargs: Дополнительные параметры конфигурации
        
    Returns:
        Результат проверки в виде словаря
    """
    config = Config(deepseek_api_key=api_key, **config_kwargs)
    
    with LLMValidator(config) as validator:
        result = validator.validate_change(change_data)
        return {
            'change_id': result.change_id,
            'validation_results': result.validation_results,
            'overall_risk': result.overall_risk,
            'overall_explanation': result.overall_explanation,
            'total_laws_checked': result.total_laws_checked,
            'contradictions_found': result.contradictions_found
        }
