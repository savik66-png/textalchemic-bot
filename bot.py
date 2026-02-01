#!/usr/bin/env python3
"""
TextAlchemic Bot - ВЕРСИЯ С ЯНДЕКС GPT
Полноценная интеграция с Yandex GPT API
"""
import os
import random
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==================== НАСТРОЙКИ ====================
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8542210651:AAG7Ze8DlRJwHrOYKPOrTqdnvJzLgcm23KQ')
YANDEX_API_KEY = os.getenv('YANDEX_API_KEY', '')  # ← СЮДА БУДЕТ КЛЮЧ ИЗ BOTHOST
YANDEX_FOLDER_ID = os.getenv('YANDEX_FOLDER_ID', 'b1gf28m0hpqbo55slm6d')  # ← ИСПРАВЛЕНО!
YANDEX_GPT_MODEL = os.getenv('YANDEX_GPT_MODEL', 'yandexgpt-lite')  # lite = дешевле

# ==================== НАСТРОЙКА ЛОГИРОВАНИЯ ====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== СТИЛИ ====================
STYLES = {
    "ice": "Лёд ❄️",
    "phoenix": "Феникс 🔥", 
    "mechanicus": "Механик ⚙️",
    "harmonicus": "Гармония 🌿",
    "architect": "Архитектор 🏛️",
    "yagpt": "Яндекс GPT 🤖"
}

# ==================== АЛГОРИТМИЧЕСКИЕ СТИЛИ (БЕЗ ИИ) ====================
def transform_ice(text: str) -> str:
    """Стиль ЛЁД - всегда 5 фактов"""
    facts = [
        "Улучшение производительности работы",
        "Оптимизация бизнес-процессов", 
        "Снижение временных затрат",
        "Улучшение качества результатов",
        "Автоматизация рутинных операций",
        "Рост продуктивности команды",
        "Упрощение рабочих процедур",
        "Стандартизация подходов"
    ]
    selected = random.sample(facts, 5)
    return f"""❄️ *КЛЮЧЕВЫЕ ФАКТЫ:*

{chr(10).join([f"{i}. {fact}." for i, fact in enumerate(selected, 1)])}

📌 *Вывод:* Текст содержит {len(text.split())} слов."""

def transform_phoenix(text: str) -> str:
    """Стиль ФЕНИКС - эмоционально с эмодзи"""
    emotions = ["🔥", "✨", "🚀", "🎯", "💥", "🌟", "🏆", "👏"]
    tags = ["#Успех", "#Инновации", "#Развитие", "#Команда", "#Будущее"]
    return f"""{random.choice(emotions)} *ЭМОЦИОНАЛЬНЫЙ АНАЛИЗ* {random.choice(emotions)}

🔥 ВАЖНО! КЛЮЧЕВОЙ МОМЕНТ! 🔥

✨ {text}

🎭 Настроение: Позитивное {random.choice(emotions)}
📈 Потенциал: Высокий {random.choice(emotions)}
💪 Рекомендация: Внедрять немедленно!

{' '.join(random.sample(tags, 3))}"""

def transform_mechanicus(text: str) -> str:
    """Стиль МЕХАНИК - технически"""
    return f"""⚙️ *ТЕХНИЧЕСКОЕ ОПИСАНИЕ*

**1. Общие сведения:**
{text}

**2. Технические параметры:**
• Надежность: Высокая
• Масштабируемость: Да  
• Сложность внедрения: Средняя

**3. Рекомендации:**
Проект требует технической доработки и тестирования.

*Документ составлен автоматически*"""

def transform_harmonicus(text: str) -> str:
    """Стиль ГАРМОНИЯ - мягко"""
    return f"""🌿 *ГАРМОНИЧНЫЙ АНАЛИЗ*

{text}

---
📖 *Комментарий:*
Представленный текст демонстрирует баланс между различными аспектами. Рекомендуется учитывать как технические, так и человеческие факторы для достижения наилучшего результата.

*В гармонии с природой и технологиями*"""

def transform_architect(text: str) -> str:
    """Стиль АРХИТЕКТОР - структурированно"""
    return f"""🏛️ *СТРУКТУРИРОВАННЫЙ ПЛАН*

**Раздел 1. Основа**
{text}

**Раздел 2. Компоненты**
1. Базовый модуль
2. Вспомогательные элементы  
3. Интеграционные решения

**Раздел 3. Внедрение**
Этап 1: Подготовка
Этап 2: Реализация
Этап 3: Контроль

*Архитектурный подход обеспечивает стабильность*"""

# ==================== ЯНДЕКС GPT ИНТЕГРАЦИЯ ====================
def check_yandex_gpt() -> bool:
    """Проверка доступности Яндекс GPT"""
    if not YANDEX_API_KEY or YANDEX_API_KEY == '':
        logger.warning("Yandex GPT: API ключ не установлен")
        return False
    
    try:
        response = requests.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
            headers={
                "Authorization": f"Api-Key {YANDEX_API_KEY}",
                "Content-Type": "application/json",
                "x-folder-id": YANDEX_FOLDER_ID
            },
            json={
                "modelUri": f"gpt://{YANDEX_FOLDER_ID}/{YANDEX_GPT_MODEL}",
                "completionOptions": {"temperature": 0.1, "maxTokens": 10},
                "messages": [{"role": "user", "text": "Привет"}]
            },
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info("✅ Yandex GPT доступен")
            return True
        else:
            logger.error(f"❌ Yandex GPT ошибка: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Yandex GPT недоступен: {e}")
        return False

def ask_yandex_gpt(text: str, style_name: str = "нейтральный") -> str:
    """Запрос к Яндекс GPT с обработкой ошибок"""
    if not YANDEX_API_KEY or YANDEX_API_KEY == '':
        return "❌ Яндекс GPT недоступен. Установите API ключ в настройках бота."
    
    # Системные промпты для разных стилей
    system_prompts = {
        "лёд": "Ты — аналитик. Отвечай фактами списком, без эмоций. Максимум 5 пунктов.",
        "феникс": "Ты — мотиватор. Используй эмодзи, восклицательные знаки, энергичный тон.",
        "механик": "Ты — технический специалист. Используй термины, структуру, конкретику.",
        "гармония": "Ты — философ. Мягкий тон, баланс, глубина, метафоры.",
        "архитектор": "Ты — планировщик. Чёткая структура, разделы, этапы, логика."
    }
    
    system_prompt = system_prompts.get(style_name.lower(), "Ты — эксперт по текстам. Улучши этот текст.")
    
    try:
        response = requests.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
            headers={
                "Authorization": f"Api-Key {YANDEX_API_KEY}",
                "Content-Type": "application/json",
                "x-folder-id": YANDEX_FOLDER_ID
            },
            json={
                "modelUri": f"gpt://{YANDEX_FOLDER_ID}/{YANDEX_GPT_MODEL}",
                "completionOptions": {"temperature": 0.7, "maxTokens": 1000},
                "messages": [
                    {"role": "system", "text": system_prompt},
                    {"role": "user", "text": text}
                ]
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('result', {}).get('alternatives', [{}])[0].get('message', {}).get('text', '')
            
            if not answer or answer.strip() == '':
                return "🤔 Яндекс GPT вернул пустой ответ. Попробуйте другой текст."
            
            return answer
            
        elif response.status_code == 401:
            return "❌ Ошибка авторизации. Проверьте правильность API ключа."
        elif response.status_code == 403:
            return f"❌ Доступ запрещён. Проверьте правильность FOLDER_ID: {YANDEX_FOLDER_ID}"
        else:
            return f"❌ Ошибка Яндекс GPT: {response.status_code}"
            
    except requests.exceptions.Timeout:
        return "⏱️ Яндекс GPT не ответил за 30 секунд. Попробуйте позже."
    except requests.exceptions.ConnectionError:
        return "🔌 Ошибка подключения к Яндекс GPT. Проверьте интернет."
    except Exception as e:
        return f"❌ Ошибка: {str(e)[:150]}"

# ==================== TELEGRAM БОТ ====================
user_states = {}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start - главное меню"""
    user_id = update.effective_user.id
    user_states[user_id] = {"step": "choose_style"}
    
    # Проверяем доступность Яндекс GPT
    yagpt_available = bool(YANDEX_API_KEY and YANDEX_API_KEY != '')
    
    keyboard = []
    for style_key, style_name in STYLES.items():
        if style_key == "yagpt" and not yagpt_available:
            continue
        keyboard.append([InlineKeyboardButton(style_name, callback_data=f"style_{style_key}")])
    
    keyboard.append([
        InlineKeyboardButton("🔍 Статус Яндекс GPT", callback_data="check_yagpt"),
        InlineKeyboardButton("📋 Инструкция", callback_data="help")
    ])
    
    status_msg = "✅ Доступен" if yagpt_available else "❌ Не настроен (нужен API ключ)"
    
    await update.message.reply_text(
        f"🤖 *TextAlchemic Bot v2.0*\n"
        f"📍 Хостинг: Bot Host\n"
        f"🤖 Яндекс GPT: {status_msg}\n"
        f"⚙️ Алгоритмы: 5 стилей\n"
        f"*Выберите стиль преобразования:*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий кнопок"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data
    
    if data.startswith("style_"):
        style = data.replace("style_", "")
        user_states[user_id] = {"style": style, "step": "waiting_text"}
        
        examples = {
            "ice": "Наш проект улучшает работу отделов на 30%",
            "phoenix": "Мы создали революционный продукт!",
            "mechanicus": "Система состоит из модулей А, Б и В",
            "harmonicus": "Баланс технологий и человеческого подхода",
            "architect": "План реализации проекта в три этапа",
            "yagpt": "Любой текст для обработки нейросетью"
        }
        
        style_name = STYLES[style]
        await query.edit_message_text(
            f"✅ Выбрано: *{style_name}*\n"
            f"Отправьте текст для преобразования.\n"
            f"💡 Пример: `{examples.get(style, 'Ваш текст здесь')}`",
            parse_mode='Markdown'
        )
    
    elif data == "check_yagpt":
        await query.edit_message_text("🔍 Проверяю доступность Яндекс GPT...")
        
        if not YANDEX_API_KEY or YANDEX_API_KEY == '':
            await query.edit_message_text(
                "⚠️ *Яндекс GPT не настроен*\n"
                "Для активации добавьте переменную `YANDEX_API_KEY` в настройках бота на BotHost.\n"
                "\n"
                "Инструкция:\n"
                "1. Зайдите в настройки бота на BotHost\n"
                "2. Найдите раздел 'Переменные окружения'\n"
                "3. Добавьте: `YANDEX_API_KEY` = ваш_ключ_от_яндекса",
                parse_mode='Markdown'
            )
            return
        
        is_available = check_yandex_gpt()
        if is_available:
            await query.edit_message_text(
                "✅ *Яндекс GPT доступен!*\n"
                f"📁 Каталог: `{YANDEX_FOLDER_ID}`\n"
                f"🤖 Модель: `{YANDEX_GPT_MODEL}`\n"
                "Теперь вы можете использовать стиль 'Яндекс GPT 🤖'",
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                "❌ *Яндекс GPT недоступен*\n"
                "Возможные причины:\n"
                "• Неправильный API ключ\n"
                "• Неправильный FOLDER_ID\n"
                "• Проблемы с интернетом",
                parse_mode='Markdown'
            )
    
    elif data == "help":
        keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="back")]]
        await query.edit_message_text(
            "📖 *ИНСТРУКЦИЯ:*\n"
            "\n"
            "*Алгоритмические стили (работают всегда):*\n"
            "• ❄️ Лёд — факты списком\n"
            "• 🔥 Феникс — эмоционально\n"
            "• ⚙️ Механик — технически\n"
            "• 🌿 Гармония — мягко\n"
            "• 🏛️ Архитектор — структурированно\n"
            "\n"
            "*Яндекс GPT (если доступен):*\n"
            "• 🤖 Яндекс GPT — нейросеть с адаптацией под стиль\n"
            "\n"
            "*Использование:*\n"
            "1. Выберите стиль через /start\n"
            "2. Отправьте текст (минимум 5 символов)\n"
            "3. Получите результат через 3-5 секунд",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif data == "back":
        await start_command(update, context)
    
    elif data == "new_text":
        if user_id in user_states and "style" in user_states[user_id]:
            style = user_states[user_id]["style"]
            user_states[user_id]["step"] = "waiting_text"
            await query.edit_message_text(
                f"🔄 Снова: *{STYLES[style]}*\n"
                f"Отправьте текст:",
                parse_mode='Markdown'
            )

async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    user_id = update.effective_user.id
    
    if user_id not in user_states or user_states[user_id].get("step") != "waiting_text":
        await update.message.reply_text("⚠️ Сначала выберите стиль через /start")
        return
    
    text = update.message.text.strip()
    
    if len(text) < 5:
        await update.message.reply_text("📝 Текст слишком короткий. Минимум 5 символов.")
        return
    
    style = user_states[user_id].get("style", "ice")
    
    # Сообщение об обработке
    processing_msg = await update.message.reply_text("⏳ Обрабатываю...")
    
    # Преобразуем текст
    if style == "yagpt":
        result = ask_yandex_gpt(text)
    else:
        # Алгоритмические стили
        style_map = {
            "ice": transform_ice,
            "phoenix": transform_phoenix,
            "mechanicus": transform_mechanicus,
            "harmonicus": transform_harmonicus,
            "architect": transform_architect
        }
        
        transform_func = style_map.get(style, transform_ice)
        result = transform_func(text)
    
    # Удаляем сообщение об обработке
    await processing_msg.delete()
    
    # Сохраняем результат
    user_states[user_id]["last_text"] = result
    
    # Кнопки для дальнейших действий
    keyboard = [
        [
            InlineKeyboardButton("🔄 Ещё текст", callback_data="new_text"),
            InlineKeyboardButton("🎨 Новый стиль", callback_data="back")
        ]
    ]
    
    # Отправляем результат
    await update.message.reply_text(
        f"✨ *{STYLES[style]}:*\n"
        f"{result}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📊 Символов: {len(result)}\n"
        f"📍 Bot Host",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ошибок"""
    logger.error(f"Ошибка: {context.error}")
    try:
        if update and update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="⚠️ Произошла ошибка. Пожалуйста, попробуйте снова."
            )
    except:
        pass

# ==================== ЗАПУСК ====================
def main():
    """Запуск бота на Bot Host"""
    print("=" * 60)
    print("🤖 TextAlchemic Bot v2.0 - ЗАПУСК")
    print("=" * 60)
    print(f"Telegram Token: {'✅ Установлен' if TELEGRAM_TOKEN else '❌ Отсутствует'}")
    print(f"Yandex API Key: {'✅ Установлен' if YANDEX_API_KEY and YANDEX_API_KEY != '' else '⚠️ Не настроен'}")
    print(f"Yandex Folder ID: {YANDEX_FOLDER_ID}")
    print(f"Yandex Model: {YANDEX_GPT_MODEL}")
    print("=" * 60)
    
    if YANDEX_API_KEY and YANDEX_API_KEY != '':
        print("🔍 Проверка Яндекс GPT...")
        if check_yandex_gpt():
            print("✅ Яндекс GPT доступен")
        else:
            print("⚠️ Яндекс GPT недоступен (но бот работает)")
    else:
        print("ℹ️ Яндекс GPT не настроен (алгоритмические стили работают)")
    
    print("=" * 60)
    print("📡 Бот работает круглосуточно")
    print("⚡ Автоматический перезапуск")
    print("=" * 60)
    
    # Создаем приложение
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Обработчики
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))
    app.add_error_handler(error_handler)
    
    # Запускаем бота
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
