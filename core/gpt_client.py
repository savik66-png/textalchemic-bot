import requests
import json
from config import YANDEX_API_KEY, YANDEX_GPT_MODEL_URI, GPT_TEMPERATURE, GPT_MAX_TOKENS

YANDEX_GPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

def call_yandex_gpt(user_message: str, model_uri: str = YANDEX_GPT_MODEL_URI, temperature: float = GPT_TEMPERATURE, max_tokens: int = GPT_MAX_TOKENS) -> str:
    """
    Отправляет запрос к YandexGPT и возвращает ответ.
    :param user_message: Текст сообщения от пользователя.
    :param model_uri: URI модели (например, gpt://b1g.../yandexgpt-lite/latest).
    :param temperature: Температура генерации.
    :param max_tokens: Максимальное количество токенов.
    :return: Ответ от GPT или сообщение об ошибке.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {YANDEX_API_KEY}"
    }

    data = {
        "modelUri": model_uri,
        "completionOptions": {
            "stream": False,
            "temperature": temperature,
            "maxTokens": str(max_tokens)
        },
        "messages": [
            {"role": "user", "text": user_message}
        ]
    }

    try:
        response = requests.post(YANDEX_GPT_URL, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()
        gpt_text = result['result']['alternatives'][0]['message']['text']
        return gpt_text.strip()

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Ошибка при запросе к YandexGPT: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"[ERROR] Тело ответа ошибки: {e.response.text}")
        return "Ошибка при обращении к ИИ. Попробуйте позже."
    except KeyError as e:
        print(f"[ERROR] Ошибка при разборе ответа YandexGPT: {e}")
        print(f"[ERROR] Полный ответ: {result}")
        return "Ошибка обработки ответа от ИИ. Попробуйте позже."
    except Exception as e:
        print(f"[ERROR] Непредвиденная ошибка при вызове GPT: {e}")
        return "Произошла непредвиденная ошибка."
