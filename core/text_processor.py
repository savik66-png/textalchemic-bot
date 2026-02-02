import json
import os
from .gpt_client import call_yandex_gpt # Импорт из того же пакета core
from config import YANDEX_GPT_MODEL_URI # Используем lite по умолчанию

# Пути к файлам данных (относительно корня проекта)
STYLES_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'styles.json')
PROMPTS_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'prompts.json')

def load_styles_and_prompts():
    """Загружает стили и промпты из JSON-файлов."""
    try:
        with open(STYLES_PATH, 'r', encoding='utf-8') as f:
            styles_data = json.load(f)
        with open(PROMPTS_PATH, 'r', encoding='utf-8') as f:
            prompts_data = json.load(f)
        # Возвращаем список стилей и словарь промптов
        return styles_data.get("styles", []), prompts_data.get("prompts", {})
    except FileNotFoundError as e:
        print(f"[ERROR] Файл не найден: {e}")
        return [], {}
    except json.JSONDecodeError as e:
        print(f"[ERROR] Ошибка парсинга JSON: {e}")
        # Печатаем начало файла для отладки
        try:
            with open(STYLES_PATH if "styles.json" in str(e) else PROMPTS_PATH, 'r', encoding='utf-8') as f:
                print(f"[DEBUG] Начало файла: {f.read()[:200]}") # Печатаем первые 200 символов
        except Exception:
            pass
        return [], {}

def process_text_with_style(original_text: str, style_id: str) -> str:
    """
    Обрабатывает текст в соответствии с выбранным стилем.
    :param original_text: Исходный текст.
    :param style_id: ID выбранного стиля (например, 'ice', 'phoenix', 'spell').
    :return: Обработанный текст или сообщение об ошибке.
    """
    styles, prompts = load_styles_and_prompts()

    if not styles or not prompts:
        return "Ошибка загрузки стилей или промптов. Попробуйте позже."

    # Находим стиль по ID
    selected_style = next((s for s in styles if s["id"] == style_id), None)
    if not selected_style:
        print(f"[DEBUG] Стиль с id '{style_id}' не найден среди загруженных.") # Отладочный вывод
        return f"Стиль '{style_id}' не найден."

    prompt_key = selected_style.get("prompt_key")
    if not prompt_key or prompt_key not in prompts:
        print(f"[DEBUG] Промпт с ключом '{prompt_key}' для стиля '{style_id}' не найден.") # Отладочный вывод
        return f"Промпт для стиля '{style_id}' не найден."

    # Получаем шаблон промпта
    prompt_template = prompts[prompt_key]
    # Формируем финальный промпт, подставляя текст
    final_prompt = prompt_template.format(text=original_text)

    # --- Выбор модели ---
    # Пока используем lite для всех, как и планировалось изначально.
    model_uri = YANDEX_GPT_MODEL_URI

    # Вызываем GPT
    result = call_yandex_gpt(final_prompt, model_uri=model_uri)
    return result

def get_available_styles_list():
    """Возвращает список доступных стилей в формате, удобном для клавиатуры."""
    styles, _ = load_styles_and_prompts()
    if not styles:
        print("[DEBUG] Не удалось загрузить стили для списка.") # Отладочный вывод
        return ["Ошибка загрузки стилей"]
    return [f"{s['id']}. {s['name']} - {s['desc']}" for s in styles]
