__version__ = "1.0.0"
__author__ = "Legal Tech Team"
__description__ = "Модуль для проверки юридической легальности изменений в документах"

from .main import LLMValidator
from .config import Config
from .clients.deepseek_client import DeepSeekClient
from .parsers.response_parser import ResponseParser
from .aggregators.risk_aggregator import RiskAggregator

__all__ = [
    "LLMValidator",
    "Config", 
    "DeepSeekClient",
    "ResponseParser",
    "RiskAggregator",
]
