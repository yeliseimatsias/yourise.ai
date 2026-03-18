import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, Optional

from .config import Config
from .schemas import ChangeInput, LawData, ValidationResult, ValidationOutput
from .clients import DeepSeekClient
from .prompts import PromptBuilder
from .db import ValidatorRepository

from embeddings.embedder import E5Embedder

# (или `from embeddings import E5Embedder`, в зависимости от вашего __init__.py в пакете)

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

        search_text = f"{change.old_text or ''} {change.new_text or ''} {change.full_chunk}"
        embeddings_list = self.embedder.embed([f"query: {search_text}"])
        embedding_vector = embeddings_list[0].tolist()

        found_laws_raw = self.db.search_similar_laws(embedding_vector, limit=3)
        found_laws = [LawData(**law) for law in found_laws_raw]

        if not found_laws:
            logger.warning("Релевантные законы не найдены.")
            return self._empty_json_result(change.change_id)

        results = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(self._check_single_law, change, law): law for law in found_laws}
            for future in as_completed(futures):
                if res := future.result():
                    results.append(res)

        # for res in results:
        #     if res.is_contradiction:
        #         try:
        #             self.db.save_validation_result(change.change_id, res.model_dump())
        #         except Exception as e:
        #             logger.error(f"Не удалось сохранить результат в БД: {e}")

        overall_risk, overall_exp = self._aggregate_risks(results)

        output = ValidationOutput(
            change_id=change.change_id,
            validation_results=results,
            overall_risk=overall_risk,
            overall_explanation=overall_exp
        )

        return output.model_dump_json(indent=2)

    def _check_single_law(self, change: ChangeInput, law: LawData) -> Optional[ValidationResult]:
        prompt = PromptBuilder.build(change, law)
        response_text = self.llm_client.generate(prompt, self.config.temperature)
        try:
            clean_json = response_text.replace('```json', '').replace('```', '').strip()
            parsed_data = json.loads(clean_json)
            return ValidationResult(law_reference=law.law_reference, law_text=law.chunk_text, **parsed_data)
        except Exception as e:
            logger.error(f"Ошибка парсинга LLM ответа: {e}")
            return None

    def _aggregate_risks(self, results: list[ValidationResult]) -> tuple[str, str]:
        high_risks = [r for r in results if r.is_contradiction and r.severity == "high"]
        if high_risks:
            return "red", f"Найдено {len(high_risks)} критических нарушений."

        medium_risks = [r for r in results if r.is_contradiction and r.severity == "medium"]
        if medium_risks:
            return "yellow", "Есть потенциальные несоответствия."

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