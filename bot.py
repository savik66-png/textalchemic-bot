#!/usr/bin/env python3
"""
TextAlchemic Bot - ВЕРСИЯ ДЛЯ BOT HOST
Оптимизирован для облачного хостинга
"""

import os
import random
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==================== НАСТРОЙКИ ====================
# Берем токен из переменных окружения Bot Host
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8500434618:AAEaMSjcIf2mJb8F2vfflO8ObG4MaTb4mQo')

# Настройки Яндекс GPT (если есть)
YANDEX_API_KEY = os.getenv('YANDEX_API_KEY', '')  # Оставьте пустым
YANDEX_FOLDER_ID = os.getenv('YANDEX_FOLDER_ID', 'b1gg2v3f25hvg3gbqbvb')
YANDEX_GPT_AVAILABLE = False

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

# ==================== АЛГОРИТМИЧЕСКИЕ СТИЛИ ====================
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
    result = ["❄️ *КЛЮЧЕВЫЕ ФАКТЫ:*\n"]
    for i, fact in enumerate(selected, 1):
        result.append(f"{i}. {fact}.")
    
    result.append(f"\n📌 *Вывод:* Текст содержит {len(text.split())} слов.")
    return "\n".join(result)

def transform_phoenix(text: str) -> str:
    """Стиль ФЕНИКС - эмоционально с эмодзи"""
    words = text.split()
    key_word = words[0] if words else "Проект"
    
    emotions = ["🔥", "✨", "🚀", "🎯", "💥", "🌟", "🏆", "👏"]
    tags = ["#Успех", "#Инновации", "#Развитие", "#Команда", "#Будущее"]
    
    result = [
        f"{random.choice(emotions)} *ЭМОЦИОНАЛЬНЫЙ АНАЛИЗ* {random.choice(emotions)}",
        "",
        f"ВАЖНО! {key_word.upper()} - ЭТО ПРОРЫВ!",
        "",
        f"✨ {text}",
        "",
        f"🎭 Настроение: Позитивное {random.choice(emotions)}",
        f"📈 Потенциал: Высокий {random.choice(emotions)}",
        f"💪 Рекомендация: Внедрять немедленно!",
        "",
        " ".join(random.sample(tags, 3))
    ]
    return "\n".join(result)

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

# ==================== YANDEX GPT ФУНКЦИИ ====================
def check_yandex_gpt():
    """Проверка доступности Яндекс GPT (неблокирующая)"""
    global YANDEX_GPT_AVAILABLE
    
    if not YANDEX_API_KEY:
        YANDEX_GPT_AVAILABLE = False
        return False
    
    try:
        # Быстрая проверка (5 секунд)
        test_response = requests.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
            headers={
                "Authorization": f"Api-Key {YANDEX_API_KEY}",
                "Content-Type": "application/json",
                "x-folder-id": YANDEX_FOLDER_ID
            },
            json={
                "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt/latest",
                "completionOptions": {"temperature": 0.1, "maxTokens": 10},
                "messages": [{"role": "user", "text": "hi"}]
            },
            timeout=5
        )
        
        YANDEX_GPT_AVAILABLE = (test_response.status_code == 200)
        logger.info(f"Yandex GPT check: {YANDEX_GPT_AVAILABLE}")
        return YANDEX_GPT_AVAILABLE
        
    except Exception as e:
        logger.warning(f"Yandex GPT check failed: {e}")
        YANDEX_GPT_AVAILABLE = False
        return False

def ask_yandex_gpt_safe(prompt: str) -> str:
    """Безопасный запрос к Яндекс GPT с обработкой ошибок"""
    if not YANDEX_API_KEY or not YANDEX_GPT_AVAILABLE:
        return "❌ Яндекс GPT недоступен. Используйте другой стиль."
    
    try:
        response = requests.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
            headers={
                "Authorization": f"Api-Key {YANDEX_API_KEY}",
                "Content-Type": "application/json",
                "x-folder-id": YANDEX_FOLDER_ID
            },
            json={
                "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt/latest",
                "completionOptions": {"temperature": 0.7, "maxTokens": 500},
                "messages": [{"role": "user", "text": prompt}]
            },
            timeout=15  # Оптимальный таймаут для Bot Host
        )
        
        if response.status_code == 200:
            result = response.json()
            text = result.get('result', {}).get('alternatives', [{}])[0].get('message', {}).get('text', '')
            return text if text else "🤔 Яндекс GPT ответил пустым сообщением"
        else:
            return f"❌ Ошибка Яндекс GPT: {response.status_code}"
            
    except requests.exceptions.Timeout:
        return "⏱️ Яндекс GPT не ответил за 15 секунд"
    except Exception as e:
        return f"❌ Ошибка подключения: {str(e)[:100]}"

# ==================== TELEGRAM БОТ ====================
user_states = {}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start - главное меню"""
    user_id = update.effective_user.id
    user_states[user_id] = {"step": "choose_style"}
    
    # Статус Яндекс GPT
    yagpt_status = "✅ Доступен" if YANDEX_GPT_AVAILABLE else "❌ Недоступен"
    
    # Клавиатура
    keyboard = []
    for style_key, style_name in STYLES.items():
        if style_key == "yagpt" and not YANDEX_GPT_AVAILABLE:
            continue
        keyboard.append([InlineKeyboardButton(style_name, callback_data=f"style_{style_key}")])
    
    keyboard.append([
        InlineKeyboardButton("🔍 Проверить Яндекс GPT", callback_data="check_yagpt"),
        InlineKeyboardButton("📋 Инструкция", callback_data="help")
    ])
    
    await update.message.reply_text(
        f"🤖 *TextAlchemic Bot*\n"
        f"📍 Запущен на Bot Host\n"
        f"🤖 Яндекс GPT: {yagpt_status}\n"
        f"⚙️ Алгоритмы: 5 стилей\n\n"
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
        
        await query.edit_message_text(
            f"✅ Выбрано: *{STYLES[style]}*\n\n"
            f"Отправьте текст для преобразования.\n\n"
            f"💡 Пример: `{examples.get(style, 'Ваш текст здесь')}`",
            parse_mode='Markdown'
        )
    
    elif data == "check_yagpt":
        if YANDEX_API_KEY:
            await query.edit_message_text("🔍 Проверяю Яндекс GPT...")
            is_available = check_yandex_gpt()
            
            if is_available:
                await query.edit_message_text(
                    "✅ Яндекс GPT доступен!\n\n"
                    "Теперь вы можете использовать стиль 'Яндекс GPT 🤖'",
                    parse_mode='Markdown'
                )
            else:
                await query.edit_message_text(
                    "❌ Яндекс GPT недоступен.\n\n"
                    "Используйте алгоритмические стили — они работают всегда!",
                    parse_mode='Markdown'
                )
        else:
            await query.edit_message_text(
                "⚠️ API-ключ Яндекс не настроен.\n\n"
                "Для использования Яндекс GPT добавьте переменную YANDEX_API_KEY в настройках Bot Host.",
                parse_mode='Markdown'
            )
    
    elif data == "help":
        keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="back")]]
        
        await query.edit_message_text(
            "📖 *ИНСТРУКЦИЯ:*\n\n"
            "*Алгоритмические стили (работают всегда):*\n"
            "• ❄️ Лёд — факты списком\n"
            "• 🔥 Феникс — эмоционально\n"
            "• ⚙️ Механик — технически\n"
            "• 🌿 Гармония — мягко\n"
            "• 🏛️ Архитектор — структурированно\n\n"
            "*Яндекс GPT (если доступен):*\n"
            "• 🤖 Яндекс GPT — нейросеть\n\n"
            "*Использование:*\n"
            "1. Выберите стиль\n"
            "2. Отправьте текст\n"
            "3. Получите результат\n"
            "4. Выберите новое действие\n\n"
            "*Bot Host:* Круглосуточная работа, автоматический перезапуск.",
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
                f"🔄 Снова: *{STYLES[style]}*\n\nОтправьте текст:",
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
        await update.message.reply_text("📝 Минимум 5 символов")
        return
    
    style = user_states[user_id].get("style", "ice")
    
    # Сообщение об обработке
    msg = await update.message.reply_text("⏳ Обрабатываю...")
    
    # Преобразуем текст
    if style == "yagpt":
        result = ask_yandex_gpt_safe(text)
    else:
        if style == "ice":
            result = transform_ice(text)
        elif style == "phoenix":
            result = transform_phoenix(text)
        elif style == "mechanicus":
            result = transform_mechanicus(text)
        elif style == "harmonicus":
            result = transform_harmonicus(text)
        elif style == "architect":
            result = transform_architect(text)
        else:
            result = f"Стиль {style} не найден"
    
    # Удаляем сообщение об обработке
    await msg.delete()
    
    # Сохраняем результат
    user_states[user_id]["last_text"] = result
    
    # Кнопки для дальнейших действий
    keyboard = [
        [
            InlineKeyboardButton("🔄 Ещё текст", callback_data="new_text"),
            InlineKeyboardButton("📋 Копировать", callback_data="copy")
        ],
        [
            InlineKeyboardButton("🎨 Новый стиль", callback_data="back"),
            InlineKeyboardButton("🔍 Проверить Яндекс GPT", callback_data="check_yagpt")
        ]
    ]
    
    # Отправляем результат
    await update.message.reply_text(
        f"✨ *{STYLES[style]}:*\n\n{result}\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📊 Символов: {len(result)}\n"
        f"🎭 Стиль: {STYLES[style]}\n"
        f"📍 Хостинг: Bot Host",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def copy_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Копирование текста"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if user_id in user_states and "last_text" in user_states[user_id]:
        text = user_states[user_id]["last_text"]
        await query.edit_message_text(
            f"📋 *Текст для копирования:*\n\n"
            f"`{text}`\n\n"
            f"ℹ️ Нажмите и удерживайте текст, чтобы скопировать.",
            parse_mode='Markdown'
        )
    else:
        await query.answer("❌ Нет текста для копирования", show_alert=True)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ошибок"""
    logger.error(f"Ошибка: {context.error}")
    try:
        if update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="⚠️ Произошла ошибка. Пожалуйста, попробуйте снова."
            )
    except:
        pass

# ==================== ЗАПУСК ====================
def main():
    """Запуск бота на Bot Host"""
    
    # Проверяем Яндекс GPT при запуске
    logger.info("Проверяю доступность Яндекс GPT...")
    if YANDEX_API_KEY:
        check_yandex_gpt()
    
    logger.info(f"Telegram Bot Token: {'установлен' if TELEGRAM_TOKEN else 'не установлен'}")
    logger.info(f"Yandex GPT: {'доступен' if YANDEX_GPT_AVAILABLE else 'недоступен'}")
    
    print("=" * 60)
    print("🤖 TextAlchemic Bot - ЗАПУЩЕН НА BOT HOST")
    print("=" * 60)
    print(f"Telegram Bot: {'✅' if TELEGRAM_TOKEN else '❌'}")
    print(f"Yandex GPT: {'✅' if YANDEX_GPT_AVAILABLE else '❌'}")
    print(f"Алгоритмы: ✅ 5 стилей")
    print("=" * 60)
    print("📡 Бот работает круглосуточно")
    print("⚡ Автоматический перезапуск")
    print("📊 Логирование включено")
    print("=" * 60)
    
    # Создаем приложение
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Обработчики
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CallbackQueryHandler(copy_handler, pattern="^copy$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))
    app.add_error_handler(error_handler)
    
    # Запускаем бота
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
