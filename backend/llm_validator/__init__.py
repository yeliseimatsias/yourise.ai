from .core import LLMValidatorPipeline
from .config import Config
from .schemas import (
    ChangeInput,
    ValidationResult,
    ValidationOutput
)

__version__ = "2.0.0" # Обновили мажорную версию из-за перехода на векторную архитектуру

# __all__ ограничивает то, что будет импортировано при `from llm_validator import *`
# и подсказывает IDE, какие классы предназначены для публичного использования.
__all__ = [
    "LLMValidatorPipeline",
    "Config",
    "ChangeInput",
    "ValidationResult",
    "ValidationOutput"
]