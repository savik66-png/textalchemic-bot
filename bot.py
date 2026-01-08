import os
import logging
import re
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s) - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")

# Стили TextAlchemic
STYLES = {
    "phoenix": {
        "name": "🔥 ФЕНИКС",
        "description": "Воскрешает скучный текст, добавляет огня и эмоций",
        "emoji": "🔥",
        "button": "🔥 Феникс"
    },
    "ice": {
        "name": "🧊 ЛЁД",
        "description": "Замораживает эмоции, оставляет чистые факты",
        "emoji": "🧊",
        "button": "🧊 Лёд"
    },
    "mechanicus": {
        "name": "📊 МЕХАНИКУС",
        "description": "Разбирает текст на шестерёнки, оставляет только рабочие детали",
        "emoji": "📊",
        "button": "📊 Механик"
    },
    "harmonicus": {
        "name": "📝 ГАРМОНИКУС",
        "description": "Балансирует текст, делает идеально читаемым",
        "emoji": "📝",
        "button": "📝 Гармония"
    },
    "architect": {
        "name": "✨ АРХИТЕКТОР",
        "description": "Строит из текста чёткое здание с этажами и комнатами",
        "emoji": "✨",
        "button": "✨ Архитектор"
    }
}

# Хранение данных пользователей
user_data_store = {}

# ==================== ФУНКЦИИ ПРЕОБРАЗОВАНИЯ ТЕКСТА ====================
def apply_phoenix(text):
    """🔥 Добавляет эмоции и энергию"""
    if not text:
        return text
    
    emotional_words = ["невероятно", "потрясающе", "фантастически", "волшебно", 
                      "восхитительно", "изумительно", "захватывающе"]
    
    words = text.split()
    
    # Добавляем эмоциональные слова
    if len(words) > 1:
        for _ in range(min(2, len(words) // 3)):
            pos = random.randint(0, len(words)-1)
            words.insert(pos, random.choice(emotional_words))
    
    result = " ".join(words)
    result = result.replace('.', '!').replace('?', '?!')
    
    # Делаем первое предложение громким
    sentences = re.split(r'[.!?]', result)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if sentences:
        sentences[0] = sentences[0].upper()
        result = '! '.join(sentences) + '!'
    
    # Добавляем эмоциональное окончание
    endings = ["Это просто ВАУ!", "Эмоции зашкаливают!", "Восхитительно!"]
    result += "\n\n" + random.choice(endings)
    
    return result

def apply_ice(text):
    """🧊 Убирает эмоции, оставляет факты"""
    if not text:
        return text
    
    emotional_words = ["очень", "крайне", "невероятно", "потрясающе", "восхитительно",
                      "ужасно", "страшно", "прекрасно", "великолепно", "изумительно"]
    
    words = text.split()
    clean_words = []
    
    for word in words:
        clean_word = word.lower()
        if clean_word not in emotional_words:
            clean_word = clean_word.replace('!', '').replace('?', '')
            clean_words.append(clean_word)
    
    result = " ".join(clean_words)
    result = result.replace('!', '.').replace('?', '.').replace('!!', '.').replace('?!', '.')
    
    # Делаем предложения короткими
    sentences = re.split(r'[.!?]', result)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    fact_sentences = []
    for sentence in sentences:
        if sentence:
            words_in_sentence = sentence.split()
            if len(words_in_sentence) > 10:
                mid = len(words_in_sentence) // 2
                fact_sentences.append(" ".join(words_in_sentence[:mid]) + ".")
                fact_sentences.append(" ".join(words_in_sentence[mid:]) + ".")
            else:
                fact_sentences.append(sentence + ".")
    
    result = " ".join(fact_sentences)
    result = result.capitalize()
    
    return result

def apply_mechanicus(text):
    """📊 Структурирует как техническую документацию"""
    if not text:
        return text
    
    words = text.split()
    
    result = "📋 ТЕХНИЧЕСКИЙ АНАЛИЗ\n"
    result += "=" * 30 + "\n\n"
    result += "СТАТИСТИКА:\n"
    result += f"• Слов: {len(words)}\n"
    result += f"• Символов: {len(text)}\n"
    result += f"• Уникальных слов: {len(set(words))}\n\n"
    
    result += "КЛЮЧЕВЫЕ СЛОВА:\n"
    key_words = words[:min(5, len(words))]
    for i, word in enumerate(key_words, 1):
        result += f"{i}. {word.upper()}\n"
    
    result += "\n" + "=" * 30
    result += "\nАнализ завершен."
    
    return result

def apply_harmonicus(text):
    """📝 Балансирует текст для лучшего чтения"""
    if not text:
        return text
    
    sentences = re.split(r'[.!?]', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return text
    
    balanced_sentences = []
    for sentence in sentences:
        words = sentence.split()
        
        if len(words) > 15:
            mid = len(words) // 2
            balanced_sentences.append(" ".join(words[:mid]))
            balanced_sentences.append(" ".join(words[mid:]))
        elif len(words) < 3:
            balanced_sentences.append(sentence + " — важный момент.")
        else:
            balanced_sentences.append(sentence)
    
    connectors = ["При этом", "Кроме того", "Таким образом", "Следовательно"]
    
    result = ""
    for i, sentence in enumerate(balanced_sentences):
        if i == 0:
            result = sentence.capitalize()
        elif i < len(connectors) and i % 2 == 0:
            result += f". {connectors[i % len(connectors)]}, {sentence.lower()}"
        else:
            result += f". {sentence.capitalize()}"
    
    result += "."
    
    return result

def apply_architect(text):
    """✨ Создает структурированный документ"""
    if not text:
        return text
    
    words = text.split()
    
    result = "📄 СТРУКТУРИРОВАННЫЙ ДОКУМЕНТ\n"
    result += "━" * 35 + "\n\n"
    
    if len(words) > 3:
        title = " ".join(words[:3]).upper()
        result += f"ЗАГОЛОВОК: {title}\n\n"
    
    result += "📌 ОСНОВНОЕ:\n"
    if len(words) > 10:
        summary = " ".join(words[:10]) + "..."
    else:
        summary = text
    result += f"{summary}\n\n"
    
    result += "🏗️ СТРУКТУРА:\n"
    
    sections = min(3, len(words) // 5)
    for i in range(sections):
        start = i * 5
        end = min(start + 5, len(words))
        if start < len(words):
            result += f"\n{i+1}. Раздел {i+1}:\n"
            result += f"   • {' '.join(words[start:end])}\n"
    
    result += "\n" + "━" * 35
    result += "\nДокумент структурирован."
    
    return result

def transform_text(text: str, style: str):
    """Главная функция преобразования текста"""
    if not text.strip():
        return "⚠️ Пустое сообщение.", ""
    
    if style == "phoenix":
        transformed = apply_phoenix(text)
        formatted = f"<b>🔥 ФЕНИКС (Эмоциональный):</b>\n\n{transformed}"
        return formatted, transformed
    
    elif style == "ice":
        transformed = apply_ice(text)
        formatted = f"<b>🧊 ЛЁД (Фактологический):</b>\n\n{transformed}"
        return formatted, transformed
    
    elif style == "mechanicus":
        transformed = apply_mechanicus(text)
        formatted = f"<b>📊 МЕХАНИКУС (Технический):</b>\n\n{transformed}"
        return formatted, transformed
    
    elif style == "harmonicus":
        transformed = apply_harmonicus(text)
        formatted = f"<b>📝 ГАРМОНИКУС (Сбалансированный):</b>\n\n{transformed}"
        return formatted, transformed
    
    elif style == "architect":
        transformed = apply_architect(text)
        formatted = f"<b>✨ АРХИТЕКТОР (Структурированный):</b>\n\n{transformed}"
        return formatted, transformed
    
    else:
        return f"<b>Оригинал:</b>\n\n{text}", text

# ==================== ТЕЛЕГРАМ БОТ ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    
    keyboard = [
        [InlineKeyboardButton("🔥 Феникс", callback_data="style_phoenix")],
        [InlineKeyboardButton("🧊 Лёд", callback_data="style_ice")],
        [InlineKeyboardButton("📊 Механик", callback_data="style_mechanicus")],
        [InlineKeyboardButton("📝 Гармония", callback_data="style_harmonicus")],
        [InlineKeyboardButton("✨ Архитектор", callback_data="style_architect")],
        [InlineKeyboardButton("ℹ️ Помощь", callback_data="help")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_html(
        f"⚗️ <b>TextAlchemic Bot</b>\n\n"
        f"Привет, {user.mention_html()}! Я превращаю текст в нужный стиль.\n\n"
        f"<b>Как использовать:</b>\n"
        f"1. Выберите стиль кнопкой ниже\n"
        f"2. Отправьте текст\n"
        f"3. Получите результат в двух сообщениях:\n"
        f"   • Первое — информация о стиле\n"
        f"   • Второе — чистый текст для копирования\n\n"
        f"<i>Алхимия слов начинается здесь!</i>",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if query.data.startswith("style_"):
        style_key = query.data.replace("style_", "")
        
        if style_key in STYLES:
            if user_id not in user_data_store:
                user_data_store[user_id] = {}
            user_data_store[user_id]['style'] = style_key
            
            style_info = STYLES[style_key]
            
            keyboard = [
                [InlineKeyboardButton("📝 Отправить текст", callback_data="send_text")],
                [InlineKeyboardButton("🔄 Выбрать другой стиль", callback_data="change_style")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"{style_info['emoji']} <b>Выбран стиль: {style_info['name']}</b>\n\n"
                f"{style_info['description']}\n\n"
                f"<i>Нажмите \"Отправить текст\" и напишите текст для преобразования.</i>",
                parse_mode='HTML',
                reply_markup=reply_markup
            )
    
    elif query.data == "send_text":
        await query.edit_message_text(
            "📝 <b>Отправьте текст для преобразования:</b>\n\n"
            "<i>Просто напишите сообщение с текстом.</i>",
            parse_mode='HTML'
        )
    
    elif query.data == "change_style":
        keyboard = [
            [InlineKeyboardButton("🔥 Феникс", callback_data="style_phoenix")],
            [InlineKeyboardButton("🧊 Лёд", callback_data="style_ice")],
            [InlineKeyboardButton("📊 Механик", callback_data="style_mechanicus")],
            [InlineKeyboardButton("📝 Гармония", callback_data="style_harmonicus")],
            [InlineKeyboardButton("✨ Архитектор", callback_data="style_architect")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🎭 <b>Выберите стиль преобразования:</b>\n\n"
            "<i>Нажмите на кнопку, чтобы выбрать стиль.</i>",
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    elif query.data == "help":
        keyboard = [
            [InlineKeyboardButton("🎭 Выбрать стиль", callback_data="change_style")],
            [InlineKeyboardButton("🚀 Начать работу", callback_data="send_text")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🛠 <b>Помощь по TextAlchemic Bot:</b>\n\n"
            "1. <b>Как использовать:</b>\n"
            "   • Выберите стиль преобразования\n"
            "   • Отправьте текст\n"
            "   • Получите результат в двух сообщениях\n\n"
            "2. <b>Стили преобразования:</b>\n"
            "   • 🔥 ФЕНИКС — для соцсетей, рекламы\n"
            "   • 🧊 ЛЁД — для отчётов, документов\n"
            "   • 📊 МЕХАНИКУС — для инструкций\n"
            "   • 📝 ГАРМОНИКУС — для блогов, статей\n"
            "   • ✨ АРХИТЕКТОР — для презентаций\n\n"
            "3. <b>Копирование текста:</b>\n"
            "   • Второе сообщение содержит чистый текст\n"
            "   • Просто выделите его и скопируйте\n\n"
            "<i>TextAlchemic: превращаем текст в золото коммуникации!</i>",
            parse_mode='HTML',
            reply_markup=reply_markup
        )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    user_id = update.effective_user.id
    user_text = update.message.text
    
    if user_id in user_data_store and 'style' in user_data_store[user_id]:
        style_key = user_data_store[user_id]['style']
        
        # Преобразуем текст
        formatted_result, clean_result = transform_text(user_text, style_key)
        
        # Сохраняем чистый текст
        user_data_store[user_id]['last_clean_text'] = clean_result
        user_data_store[user_id]['original_text'] = user_text
        
        # Отправляем информационное сообщение
        keyboard = [
            [InlineKeyboardButton("🔄 Преобразовать ещё", callback_data="send_text")],
            [InlineKeyboardButton("🎭 Сменить стиль", callback_data="change_style")],
            [InlineKeyboardButton("📋 Отправить чистый текст", callback_data="send_clean_text")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            formatted_result,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        
        # Отправляем чистый текст для копирования
        await update.message.reply_text(
            f"📋 <b>Чистый текст для копирования:</b>\n\n"
            f"{clean_result}\n\n"
            f"<i>Просто выделите этот текст и скопируйте.</i>",
            parse_mode='HTML'
        )
    else:
        keyboard = [
            [InlineKeyboardButton("🎭 Выбрать стиль", callback_data="change_style")],
            [InlineKeyboardButton("ℹ️ Помощь", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "⚠️ <b>Сначала выберите стиль преобразования!</b>\n\n"
            "Нажмите кнопку ниже, чтобы выбрать стиль.",
            parse_mode='HTML',
            reply_markup=reply_markup
        )

async def send_clean_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет сохраненный чистый текст"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if user_id in user_data_store and 'last_clean_text' in user_data_store[user_id]:
        clean_text = user_data_store[user_id]['last_clean_text']
        
        await query.message.reply_text(
            f"📋 <b>Чистый текст для копирования:</b>\n\n"
            f"{clean_text}",
            parse_mode='HTML'
        )
    else:
        await query.message.reply_text(
            "⚠️ <b>Нет сохраненного текста</b>\n\n"
            "Отправьте текст для преобразования сначала.",
            parse_mode='HTML'
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    keyboard = [
        [InlineKeyboardButton("🎭 Выбрать стиль", callback_data="change_style")],
        [InlineKeyboardButton("🚀 Начать работу", callback_data="send_text")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🛠 <b>Помощь по TextAlchemic Bot:</b>\n\n"
        "1. <b>Команды:</b>\n"
        "   /start — начать работу\n"
        "   /help — эта справка\n\n"
        "2. <b>Как использовать:</b>\n"
        "   • Нажмите /start\n"
        "   • Выберите стиль из 5 вариантов\n"
        "   • Отправьте текст\n"
        "   • Получите результат в двух сообщениях\n\n"
        "3. <b>Копирование текста:</b>\n"
        "   • Второе сообщение содержит чистый текст\n"
        "   • Просто выделите и скопируйте\n\n"
        "<i>Алхимия слов начинается здесь!</i>",
        parse_mode='HTML',
        reply_markup=reply_markup
    )

async def demo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Демонстрация работы (команда /demo)"""
    demo_text = "Наш продукт значительно повышает эффективность работы команды"
    
    demo_result = (
        "⚗️ <b>ДЕМОНСТРАЦИЯ TEXTALCHEMIC:</b>\n\n"
        f"<b>Исходный текст:</b>\n«{demo_text}»\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "<b>Как работает:</b>\n"
        "1. Вы выбираете стиль\n"
        "2. Отправляете текст\n"
        "3. Получаете два сообщения:\n"
        "   • Информация о стиле\n"
        "   • Чистый текст для копирования\n\n"
        "<i>Выберите стиль и попробуйте сами!</i>"
    )
    
    keyboard = [
        [InlineKeyboardButton("🎭 Выбрать стиль", callback_data="change_style")],
        [InlineKeyboardButton("🚀 Попробовать", callback_data="send_text")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        demo_result,
        parse_mode='HTML',
        reply_markup=reply_markup
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Ошибка: {context.error}")

def main():
    """Основная функция запуска бота"""
    if not TOKEN:
        logger.error("❌ Токен не найден! Проверьте переменную окружения BOT_TOKEN")
        return
    
    print("⚗️ TextAlchemic Bot запускается...")
    print(f"🔑 Токен: {TOKEN[:10]}...")
    
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("demo", demo_command))
    
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(CallbackQueryHandler(send_clean_text_handler, pattern="send_clean_text"))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    application.add_error_handler(error_handler)
    
    print("🤖 TextAlchemic запущен и готов к алхимии текстов!")
    print("ℹ️  Напишите боту: /start для начала работы")
    application.run_polling()

if __name__ == '__main__':
    main()
