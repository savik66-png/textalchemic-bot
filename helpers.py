"""
Вспомогательные функции
"""

import re
from typing import Optional

def validate_text_length(text: str, min_length: int = 10, max_length: int = 4000) -> Optional[str]:
    """
    Проверить длину текста
    
    Args:
        text: Текст для проверки
        min_length: Минимальная длина
        max_length: Максимальная длина
        
    Returns:
        Optional[str]: Сообщение об ошибке или None если всё ок
    """
    
    text_len = len(text.strip())
    
    if text_len < min_length:
        return f"📝 Минимум {min_length} символов. Сейчас: {text_len}"
    
    if text_len > max_length:
        return f"📝 Максимум {max_length} символов. Сейчас: {text_len}"
    
    return None

def clean_text_for_display(text: str, max_length: int = 200) -> str:
    """
    Очистить текст для отображения
    
    Args:
        text: Исходный текст
        max_length: Максимальная длина для preview
        
    Returns:
        str: Очищенный текст
    """
    
    # Удаляем лишние пробелы
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Обрезаем если слишком длинный
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    return text