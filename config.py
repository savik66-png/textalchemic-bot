"""
Конфигурация приложения TextAlchemic Bot
"""
import os

class Config:
    """Класс конфигурации приложения"""
    
    # ==================== КЛЮЧИ API ====================
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
    FOLDER_ID = os.getenv("FOLDER_ID", "b1gf28m0hpqbo55slm6d")
    
    # ==================== НАСТРОЙКИ ПРИЛОЖЕНИЯ ====================
    MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", "4000"))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # ==================== НАСТРОЙКИ YANDEX GPT ====================
    YANDEX_GPT_MODEL = os.getenv("YANDEX_GPT_MODEL", "yandexgpt-lite")
    YANDEX_GPT_TEMPERATURE = float(os.getenv("YANDEX_GPT_TEMPERATURE", "0.7"))
    YANDEX_GPT_MAX_TOKENS = int(os.getenv("YANDEX_GPT_MAX_TOKENS", "1500"))
    
    # ==================== ПУТИ К ФАЙЛАМ ====================
    DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
    PROMPTS_FILE = os.path.join(DATA_DIR, "prompts.json")
    STYLES_FILE = os.path.join(DATA_DIR, "styles.json")
    
    @classmethod
    def validate(cls):
        """Проверка корректности конфигурации"""
        errors = []
        
        if not cls.TELEGRAM_TOKEN:
            errors.append("TELEGRAM_TOKEN не установлен")
        if not cls.YANDEX_API_KEY:
            errors.append("YANDEX_API_KEY не установлен (стили с ИИ не будут работать)")
        if not cls.FOLDER_ID:
            errors.append("FOLDER_ID не установлен")
        
        return errors

    @classmethod
    def print_config(cls):
        """Вывод текущей конфигурации (без ключей)"""
        errors = cls.validate()
        status = "❌ Ошибки" if errors else "✅ Готов к работе"
        
        return f"""
{'='*60}
🤖 TextAlchemic Bot — Конфигурация
{'='*60}
Статус: {status}
Telegram Token: {'✅ Установлен' if cls.TELEGRAM_TOKEN else '❌ Отсутствует'}
Yandex API Key: {'✅ Установлен' if cls.YANDEX_API_KEY else '⚠️ Не установлен (только алгоритмические стили)'}
Folder ID: {cls.FOLDER_ID}
Модель: {cls.YANDEX_GPT_MODEL}
{'='*60}
"""