"""
Клиент для DeepSeek R1 через OpenRouter API.

Поддерживает retry-логику, таймауты и обработку ошибок.
"""

import requests
import json
import time
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Структурированный ответ от LLM."""
    success: bool
    content: str = ""
    tokens_used: int = 0
    error: str = ""
    raw_response: Optional[Dict] = None


class DeepSeekClient:
    """
    Клиент для DeepSeek R1 через OpenRouter API.
    
    Args:
        api_key: API ключ для OpenRouter
        base_url: Базовый URL API
        model: Название модели
        timeout: Таймаут запроса в секундах
    """
    
    def __init__(
        self, 
        api_key: str, 
        base_url: str = "https://openrouter.ai/api/v1",
        model: str = "deepseek/deepseek-r1",
        timeout: int = 30
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = timeout
        
        # Статистика для мониторинга
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_tokens': 0,
            'total_time': 0.0
        }
    
    def generate(
        self, 
        prompt: str, 
        temperature: float = 0.1,
        max_tokens: int = 2000,
        require_json: bool = True
    ) -> LLMResponse:
        """
        Отправляет запрос к DeepSeek R1.
        
        Args:
            prompt: Текст запроса
            temperature: Температура генерации (0.0-1.0)
            max_tokens: Максимальное количество токенов
            require_json: Требовать JSON-формат ответа
            
        Returns:
            LLMResponse с результатом или ошибкой
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://yourise.app",
            "X-Title": "LLM Validator"
        }
        
        messages = [{"role": "user", "content": prompt}]
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if require_json:
            data["response_format"] = {"type": "json_object"}
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            
            elapsed = time.time() - start_time
            self.stats['total_requests'] += 1
            self.stats['total_time'] += elapsed
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                tokens = result.get('usage', {}).get('total_tokens', 0)
                
                self.stats['successful_requests'] += 1
                self.stats['total_tokens'] += tokens
                
                logger.debug(f"Запрос успешен: {tokens} токенов за {elapsed:.2f}s")
                
                return LLMResponse(
                    success=True,
                    content=content,
                    tokens_used=tokens,
                    raw_response=result
                )
            else:
                self.stats['failed_requests'] += 1
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"Ошибка API: {error_msg}")
                
                return LLMResponse(
                    success=False,
                    error=error_msg,
                    raw_response={"status_code": response.status_code, "text": response.text}
                )
                
        except requests.exceptions.Timeout:
            self.stats['failed_requests'] += 1
            logger.error(f"Таймаут запроса ({self.timeout}s)")
            return LLMResponse(success=False, error=f"Таймаут запроса ({self.timeout}s)")
            
        except requests.exceptions.RequestException as e:
            self.stats['failed_requests'] += 1
            logger.error(f"Ошибка сети: {str(e)}")
            return LLMResponse(success=False, error=f"Ошибка сети: {str(e)}")
            
        except Exception as e:
            self.stats['failed_requests'] += 1
            logger.error(f"Неожиданная ошибка: {str(e)}")
            return LLMResponse(success=False, error=f"Неожиданная ошибка: {str(e)}")
    
    def generate_with_retry(
        self, 
        prompt: str, 
        max_retries: int = 3,
        base_delay: float = 1.0,
        **kwargs
    ) -> LLMResponse:
        """
        Генерация с повторными попытками при ошибках.
        
        Args:
            prompt: Текст запроса
            max_retries: Максимальное количество попыток
            base_delay: Базовая задержка между попытками (экспоненциальный backoff)
            **kwargs: Дополнительные параметры для generate()
            
        Returns:
            LLMResponse с результатом
        """
        last_error = ""
        
        for attempt in range(max_retries):
            result = self.generate(prompt, **kwargs)
            
            if result.success:
                return result
            
            last_error = result.error
            
            # Не делаем retry на 4xx ошибки (кроме 429 - rate limit)
            if result.raw_response:
                status_code = result.raw_response.get('status_code', 0)
                if 400 <= status_code < 500 and status_code != 429:
                    logger.warning(f"Клиентская ошибка {status_code}, retry не требуется")
                    break
            
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                logger.info(f"Попытка {attempt + 1} не удалась, повтор через {delay:.1f}s...")
                time.sleep(delay)
        
        return LLMResponse(
            success=False,
            error=f"Все {max_retries} попыток не удались. Последняя ошибка: {last_error}"
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Возвращает статистику использования."""
        stats = self.stats.copy()
        if stats['total_requests'] > 0:
            stats['avg_time_per_request'] = stats['total_time'] / stats['total_requests']
            stats['success_rate'] = stats['successful_requests'] / stats['total_requests']
        else:
            stats['avg_time_per_request'] = 0.0
            stats['success_rate'] = 0.0
        return stats
    
    def reset_stats(self):
        """Сбрасывает статистику."""
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_tokens': 0,
            'total_time': 0.0
        }