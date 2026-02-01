"""
Клиент для работы с Yandex GPT API
Отвечает только за общение с нейросетью
"""

import aiohttp
import logging
from typing import Optional
from config import Config

logger = logging.getLogger(__name__)

class YandexGPTClient:
    """Клиент для Yandex GPT API"""
    
    def __init__(self):
        self.api_key = Config.YANDEX_API_KEY
        self.folder_id = Config.FOLDER_ID
        self.base_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        self.timeout = aiohttp.ClientTimeout(total=Config.REQUEST_TIMEOUT)
        
    async def process_text(self, style: str, text: str, system_prompt: str) -> str:
        """
        Обработать текст с помощью Yandex GPT
        
        Args:
            style: Идентификатор стиля (для логирования)
            text: Текст для обработки
            system_prompt: Системный промпт
            
        Returns:
            str: Результат обработки или сообщение об ошибке
        """
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {self.api_key}",
            "x-folder-id": self.folder_id,
        }
        
        data = {
            "modelUri": f"gpt://{self.folder_id}/yandexgpt-lite",
            "completionOptions": {
                "stream": False,
                "temperature": 0.7,
                "maxTokens": 1500,
            },
            "messages": [
                {"role": "system", "text": system_prompt},
                {"role": "user", "text": text},
            ],
        }
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(self.base_url, headers=headers, json=data) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        text_result = result.get("result", {}).get("alternatives", [{}])[0].get("message", {}).get("text", "")
                        
                        if not text_result:
                            logger.warning(f"Пустой ответ от Yandex GPT для стиля: {style}")
                            return "⚠️ Нейросеть вернула пустой ответ"
                        
                        logger.info(f"Успешный запрос к Yandex GPT, стиль: {style}")
                        return text_result
                    
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка Yandex GPT: {response.status}, {error_text}")
                        return f"❌ Ошибка Yandex GPT ({response.status})"
                        
        except aiohttp.ClientTimeoutError:
            logger.error(f"Таймаут запроса к Yandex GPT, стиль: {style}")
            return "⏳ Таймаут запроса к нейросети. Попробуйте позже."
            
        except Exception as e:
            logger.error(f"Ошибка соединения с Yandex GPT: {e}")
            return f"💥 Ошибка соединения: {str(e)[:100]}"
