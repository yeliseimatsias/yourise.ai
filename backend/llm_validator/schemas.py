from pydantic import BaseModel
from typing import List, Optional, Literal

class LawData(BaseModel):
    """Модель для найденного в БД закона."""
    law_reference: str
    chunk_text: str
    hierarchy_level: int
    similarity: float

class ChangeInput(BaseModel):
    """Входные данные от пользователя/фронтенда."""
    change_id: str
    session_id: str
    type: Literal["added", "deleted", "modified", "moved_and_modified"]
    element_number: str = "не указан"
    old_text: Optional[str] = None
    new_text: Optional[str] = None
    full_chunk: str
    document_type: str
    document_level: int

class ValidationResult(BaseModel):
    """Результат проверки одного закона LLM-моделью."""
    law_reference: str
    law_text: str
    contradiction_type: Literal["direct", "indirect", "none", "unknown"]
    is_contradiction: bool
    confidence: float
    explanation: str
    quote_from_law: str = ""
    suggestion: Optional[str] = None
    severity: Literal["high", "medium", "low"] = "low"

class ValidationOutput(BaseModel):
    """Итоговый ответ пайплайна."""
    change_id: str
    validation_results: List[ValidationResult]
    overall_risk: Literal["red", "yellow", "green"]
    overall_explanation: str