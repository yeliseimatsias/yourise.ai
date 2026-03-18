"""
Агрегатор результатов проверки.

Объединяет результаты проверки по нескольким законам и определяет общий риск.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Уровни риска."""
    RED = "red"      # Высокий риск - прямые противоречия
    YELLOW = "yellow"  # Средний риск - потенциальные проблемы
    GREEN = "green"   # Низкий риск - нет противоречий


class SeverityLevel(Enum):
    """Уровни серьезности нарушения."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class AggregatedRisk:
    """Результат агрегации рисков."""
    overall_risk: str  # red, yellow, green
    overall_explanation: str
    total_checks: int
    contradictions_found: int
    high_severity_count: int
    medium_severity_count: int
    low_severity_count: int
    confidence_avg: float


class RiskAggregator:
    """Агрегирует результаты проверки по нескольким законам."""
    
    # Пороги для определения уровня риска
    HIGH_CONFIDENCE_THRESHOLD = 0.8
    MEDIUM_CONFIDENCE_THRESHOLD = 0.6
    
    @classmethod
    def aggregate(cls, results: List[Dict[str, Any]]) -> AggregatedRisk:
        """
        Определяет общий риск по всем проверкам.
        
        Args:
            results: Список результатов проверки по каждому закону
            
        Returns:
            AggregatedRisk с общей оценкой
        """
        if not results:
            return AggregatedRisk(
                overall_risk=RiskLevel.GREEN.value,
                overall_explanation="Нет данных для проверки",
                total_checks=0,
                contradictions_found=0,
                high_severity_count=0,
                medium_severity_count=0,
                low_severity_count=0,
                confidence_avg=0.0
            )
        
        total_checks = len(results)
        contradictions = [r for r in results if r.get('is_contradiction', False)]
        contradictions_found = len(contradictions)
        
        # Подсчитываем серьезность
        severity_counts = {"high": 0, "medium": 0, "low": 0}
        for r in results:
            sev = r.get('severity', 'low')
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        # Средняя уверенность
        confidences = [r.get('confidence', 0) for r in results]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Определяем общий риск
        risk_level, explanation = cls._determine_risk_level(results, contradictions)
        
        logger.info(f"Агрегация: {contradictions_found}/{total_checks} противоречий, "
                   f"риск: {risk_level}")
        
        return AggregatedRisk(
            overall_risk=risk_level,
            overall_explanation=explanation,
            total_checks=total_checks,
            contradictions_found=contradictions_found,
            high_severity_count=severity_counts["high"],
            medium_severity_count=severity_counts["medium"],
            low_severity_count=severity_counts["low"],
            confidence_avg=avg_confidence
        )
    
    @classmethod
    def _determine_risk_level(cls, all_results: List[Dict], 
                              contradictions: List[Dict]) -> tuple[str, str]:
        """Определяет уровень риска на основе результатов."""
        
        # RED: Есть прямые противоречия с высокой уверенностью
        high_confidence_direct = [
            r for r in contradictions 
            if r.get('contradiction_type') == 'direct' 
            and r.get('confidence', 0) >= cls.HIGH_CONFIDENCE_THRESHOLD
        ]
        
        if high_confidence_direct:
            laws = [r.get('law_reference', 'неизвестно') for r in high_confidence_direct[:2]]
            return (
                RiskLevel.RED.value,
                f"Обнаружены прямые противоречия законодательству ({', '.join(laws)}). "
                f"Требуется срочное исправление."
            )
        
        # YELLOW: Есть прямые противоречия со средней уверенностью или косвенные
        medium_confidence_direct = [
            r for r in contradictions
            if r.get('contradiction_type') == 'direct'
            and r.get('confidence', 0) >= cls.MEDIUM_CONFIDENCE_THRESHOLD
        ]
        
        indirect_contradictions = [
            r for r in contradictions
            if r.get('contradiction_type') == 'indirect'
            and r.get('confidence', 0) >= cls.MEDIUM_CONFIDENCE_THRESHOLD
        ]
        
        if medium_confidence_direct or indirect_contradictions:
            issues = []
            if medium_confidence_direct:
                issues.append("потенциальные прямые противоречия")
            if indirect_contradictions:
                issues.append("косвенные противоречия")
            
            return (
                RiskLevel.YELLOW.value,
                f"Обнаружены {' и '.join(issues)}. Рекомендуется проверка юристом."
            )
        
        # YELLOW: Низкая уверенность в ответах (систематическая проблема)
        low_confidence_count = sum(
            1 for r in all_results 
            if r.get('confidence', 1) < cls.MEDIUM_CONFIDENCE_THRESHOLD
        )
        if low_confidence_count >= 2:
            return (
                RiskLevel.YELLOW.value,
                "Низкая уверенность в результатах проверки. Рекомендуется ручная проверка."
            )
        
        # GREEN: Нет противоречий
        return (
            RiskLevel.GREEN.value,
            "Изменение не противоречит проверенным нормам законодательства."
        )
    
    @classmethod
    def calculate_severity(cls, result: Dict[str, Any]) -> str:
        """
        Определяет серьезность конкретного нарушения.
        
        Args:
            result: Результат проверки одного закона
            
        Returns:
            Уровень серьезности: high, medium, low
        """
        contradiction_type = result.get('contradiction_type', 'none')
        confidence = result.get('confidence', 0)
        is_contradiction = result.get('is_contradiction', False)
        
        if not is_contradiction or contradiction_type == 'none':
            return SeverityLevel.LOW.value
        
        if contradiction_type == 'direct':
            if confidence >= 0.9:
                return SeverityLevel.HIGH.value
            elif confidence >= 0.7:
                return SeverityLevel.MEDIUM.value
            else:
                return SeverityLevel.LOW.value
        
        if contradiction_type == 'indirect':
            if confidence >= 0.8:
                return SeverityLevel.MEDIUM.value
            else:
                return SeverityLevel.LOW.value
        
        return SeverityLevel.LOW.value
    
    @classmethod
    def get_priority_issues(cls, results: List[Dict[str, Any]], 
                           min_severity: str = "medium") -> List[Dict[str, Any]]:
        """
        Возвращает список приоритетных проблем.
        
        Args:
            results: Все результаты проверки
            min_severity: Минимальный уровень серьезности для включения
            
        Returns:
            Отфильтрованный и отсортированный список проблем
        """
        severity_order = {"high": 3, "medium": 2, "low": 1}
        min_level = severity_order.get(min_severity, 2)
        
        # Фильтруем только проблемы с нужной серьезностью
        issues = [
            r for r in results 
            if r.get('is_contradiction', False)
            and severity_order.get(r.get('severity', 'low'), 0) >= min_level
        ]
        
        # Сортируем по серьезности (убывание) и уверенности (убывание)
        issues.sort(key=lambda x: (
            severity_order.get(x.get('severity', 'low'), 0),
            x.get('confidence', 0)
        ), reverse=True)
        
        return issues