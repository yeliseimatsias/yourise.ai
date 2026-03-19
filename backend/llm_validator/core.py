# llm_validator/core.py

import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, Optional, List

from .config import Config
from .schemas import ChangeInput, LawData, ValidationResult, ValidationOutput
from .clients import DeepSeekClient
from .prompts import PromptBuilder
from .db import ValidatorRepository

from backend.embeddings.embedder import E5Embedder

logger = logging.getLogger(__name__)


class LLMValidatorPipeline:
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.config.validate()

        self.llm_client = DeepSeekClient(
            api_key=self.config.deepseek_api_key,
            base_url=self.config.deepseek_base_url,
            model=self.config.deepseek_model,
            timeout=self.config.request_timeout
        )

        self.embedder = E5Embedder(model_name=self.config.embedder_model)
        self.db = ValidatorRepository(self.config.db_config)

    def process_change_to_json(self, raw_data: Dict[str, Any]) -> str:
        """Главный метод: Векторный поиск -> LLM проверка -> Сохранение -> JSON"""
        change = ChangeInput(**raw_data)
        logger.info(f"Начало обработки: {change.change_id}")

        # Формируем текст для поиска (используем полный контекст)
        search_text = f"{change.old_text or ''} {change.new_text or ''} {change.full_chunk}"
        embeddings_list = self.embedder.embed([f"query: {search_text}"])
        embedding_vector = embeddings_list[0].tolist()

        # Ищем похожие законы в БД
        found_laws_raw = self.db.search_similar_laws(embedding_vector, limit=3)
        found_laws = [LawData(**law) for law in found_laws_raw]

        if not found_laws:
            logger.warning("Релевантные законы не найдены.")
            return self._empty_json_result(change.change_id)

        # Параллельно проверяем каждый закон
        results = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(self._check_single_law, change, law): law for law in found_laws}
            for future in as_completed(futures):
                if res := future.result():
                    results.append(res)

        # Сохраняем результаты в БД (только если есть противоречия)
        for res in results:
            if res and res.is_contradiction:
                try:
                    self.db.save_validation_result(change.change_id, res.model_dump())
                except Exception as e:
                    logger.error(f"Не удалось сохранить результат в БД: {e}")

        # Агрегируем общий риск
        overall_risk, overall_exp = self._aggregate_risks(results)

        output = ValidationOutput(
            change_id=change.change_id,
            validation_results=results,
            overall_risk=overall_risk,
            overall_explanation=overall_exp
        )

        return output.model_dump_json(indent=2)

    def _check_single_law(self, change: ChangeInput, law: LawData) -> Optional[ValidationResult]:
        """
        Проверяет одно изменение против одного закона.
        Возвращает ValidationResult или None в случае ошибки.
        """
        prompt = PromptBuilder.build(change, law)
        
        # Отправляем запрос к LLM
        response_text = self.llm_client.generate(prompt, self.config.temperature)
        
        # Если ответ пустой или явная ошибка
        if not response_text or "ERROR" in response_text:
            logger.warning(f"⚠️ LLM вернул ошибку для закона {law.law_reference}")
            return self._create_fallback_result(law, "LLM временно недоступен")

        # Логируем ответ для отладки (обрезаем до 200 символов)
        logger.debug(f"📥 Ответ LLM для {law.law_reference[:30]}: {response_text[:200]}")

        try:
            # Очищаем ответ от возможных markdown-маркеров
            clean_json = response_text.replace('```json', '').replace('```', '').strip()
            parsed_data = json.loads(clean_json)

            # Проверяем наличие всех обязательных полей
            required_fields = ['contradiction_type', 'is_contradiction', 'confidence', 'explanation']
            missing_fields = [f for f in required_fields if f not in parsed_data]
            
            if missing_fields:
                logger.warning(f"⚠️ В ответе отсутствуют поля: {missing_fields}")
                return self._create_fallback_result(law, f"Отсутствуют поля: {missing_fields}")

            # Проверяем корректность значений
            if parsed_data['contradiction_type'] not in ['direct', 'indirect', 'none']:
                parsed_data['contradiction_type'] = 'none'
            
            if not isinstance(parsed_data['is_contradiction'], bool):
                parsed_data['is_contradiction'] = False
            
            if not isinstance(parsed_data['confidence'], (int, float)):
                parsed_data['confidence'] = 0.5

            # Создаем результат с данными от LLM
            return ValidationResult(
                law_reference=law.law_reference,
                law_text=law.chunk_text,
                **parsed_data
            )

        except json.JSONDecodeError as e:
            logger.error(f"❌ Ошибка парсинга JSON: {e}")
            logger.debug(f"Ответ LLM: {response_text[:200]}")
            return self._create_fallback_result(law, "Ошибка парсинга ответа LLM")
            
        except Exception as e:
            logger.error(f"❌ Неизвестная ошибка: {e}")
            return self._create_fallback_result(law, f"Ошибка: {str(e)[:50]}")

    def _create_fallback_result(self, law: LawData, reason: str) -> ValidationResult:
        """
        Создает запасной результат (зеленый) при ошибках.
        """
        return ValidationResult(
            law_reference=law.law_reference,
            law_text=law.chunk_text,
            contradiction_type="none",
            is_contradiction=False,
            confidence=0.5,
            explanation=f"LLM не предоставил анализ: {reason}",
            quote_from_law="",
            suggestion="",
            severity="low"
        )

    def _aggregate_risks(self, results: List[ValidationResult]) -> tuple[str, str]:
        """
        Агрегирует результаты проверки по всем законам.
        Возвращает (overall_risk, explanation)
        """
        if not results:
            return "green", "Нет данных для проверки"

        # Сначала ищем критические нарушения
        high_risks = [r for r in results if r.is_contradiction and r.severity == "high"]
        if high_risks:
            return "red", f"Найдено {len(high_risks)} критических нарушений."

        # Потом средние
        medium_risks = [r for r in results if r.is_contradiction and r.severity == "medium"]
        if medium_risks:
            return "yellow", "Есть потенциальные несоответствия."

        # Если есть хоть какие-то противоречия (даже low)
        any_contradictions = [r for r in results if r.is_contradiction]
        if any_contradictions:
            return "yellow", "Обнаружены незначительные противоречия."

        # Всё хорошо
        return "green", "Изменение соответствует найденным законам."

    def _empty_json_result(self, change_id: str) -> str:
        """Возвращает зеленый JSON, если база ничего не нашла."""
        output = ValidationOutput(
            change_id=change_id,
            validation_results=[],
            overall_risk="green",
            overall_explanation="Нет релевантных законов для проверки."
        )
        return output.model_dump_json(indent=2)