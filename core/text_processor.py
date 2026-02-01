"""
Обработчик текста
Связывает стили, промпты и нейросеть
"""
import json
import os
from typing import Dict, Any
from core.gpt_client import YandexGPTClient

class TextProcessor:
    """Обработчик текста"""
    
    def __init__(self):
        self.gpt_client = YandexGPTClient()
        self._load_data()
    
    def _load_data(self):
        """Загрузка промптов и стилей"""
        # Определяем путь к папке data относительно текущего файла
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        data_dir = os.path.join(project_root, 'data')
        
        prompts_path = os.path.join(data_dir, 'prompts.json')
        styles_path = os.path.join(data_dir, 'styles.json')
        
        try:
            with open(prompts_path, 'r', encoding='utf-8') as f:
                self.prompts = json.load(f)
            
            with open(styles_path, 'r', encoding='utf-8') as f:
                # Убираем пробелы из ключей при загрузке
                raw_styles = json.load(f)
                self.styles = {
                    key.strip(): {
                        k.strip(): v.strip() if isinstance(v, str) else v 
                        for k, v in value.items()
                    }
                    for key, value in raw_styles.items()
                }
                
        except FileNotFoundError as e:
            raise Exception(f"Файл данных не найден: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"Ошибка в формате JSON файла: {e}")
    
    def get_all_styles(self) -> Dict[str, Dict[str, str]]:
        """Получить все доступные стили"""
        return self.styles
    
    def get_style_info(self, style_id: str) -> Dict[str, str]:
        """Получить информацию о стиле"""
        return self.styles.get(style_id, {"name": "Неизвестный стиль", "desc": ""})
    
    def get_prompt(self, style_id: str) -> str:
        """Получить промпт для стиля"""
        return self.prompts.get(style_id, "")
    
    async def process(self, style_id: str, text: str) -> str:
        """
        Обработать текст в заданном стиле
        
        Args:
            style_id: Идентификатор стиля
            text: Текст для обработки
            
        Returns:
            str: Результат обработки
        """
        
        # Проверяем, что стиль существует
        if style_id not in self.prompts:
            return f"❌ Стиль '{style_id}' не найден"
        
        # Получаем промпт
        system_prompt = self.prompts[style_id]
        
        # Обрабатываем через нейросеть
        try:
            result = await self.gpt_client.process_text(style_id, text, system_prompt)
            return result
        except Exception as e:
            return f"❌ Ошибка обработки: {str(e)[:150]}"