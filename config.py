import os
from dotenv import load_dotenv

# load_dotenv() # BotHost не использует .env файл, но может быть полезно для локальной отладки
# if os.path.exists('.env'): # Проверка на наличие .env файла
#     load_dotenv()

# --- Переменные окружения ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
YANDEX_FOLDER_ID = os.getenv("FOLDER ID")

# --- Конфигурация GPT ---
# Позволим переопределить модель через переменную окружения, иначе используем lite по умолчанию
YANDEX_GPT_MODEL_URI = os.getenv("YANDEX_GPT_MODEL_URI", f"gpt://{FOLDER ID}/yandexgpt-lite/latest")
GPT_TEMPERATURE = float(os.getenv("GPT_TEMPERATURE", "0.6"))
GPT_MAX_TOKENS = int(os.getenv("GPT_MAX_TOKENS", "500"))

# --- Проверка наличия обязательных переменных ---
missing_vars = []
for var_name, var_value in [("BOT_TOKEN", BOT_TOKEN), ("YANDEX_API_KEY", YANDEX_API_KEY), ("FOLDER ID", FOLDER ID)]:
    if not var_value:
        missing_vars.append(var_name)

if missing_vars:
    raise ValueError(f"Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}")

print(f"[CONFIG] Bot Token Loaded: {'Yes' if BOT_TOKEN else 'No'}")
print(f"[CONFIG] Yandex API Key Loaded: {'Yes' if YANDEX_API_KEY else 'No'}")
print(f"[CONFIG] Yandex Folder ID: {FOLDER ID}")
print(f"[CONFIG] Yandex Model URI: {YANDEX_GPT_MODEL_URI}")

# Экспортируем для использования в других модулях
__all__ = [
    "BOT_TOKEN",
    "YANDEX_API_KEY",
    "FOLDER ID",
    "YANDEX_GPT_MODEL_URI",
    "GPT_TEMPERATURE",
    "GPT_MAX_TOKENS"
]


