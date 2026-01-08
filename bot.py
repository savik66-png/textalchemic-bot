import os
import logging
import re
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")

# Стили
STYLES = {
    "phoenix": {
        "name": "🔥 ФЕНИКС",
        "description": "Эмоциональный, энергичный текст для соцсетей и рекламы",
        "emoji": "🔥",
        "button": "🔥 Феникс"
    },
    "ice": {
        "name": "🧊 ЛЁД",
        "description": "Фактологический, нейтральный текст для отчётов",
        "emoji": "🧊",
        "button": "🧊 Лёд"
    },
    "mechanicus": {
        "name": "📊 МЕХАНИКУС",
        "description": "Технический документ со структурированными данными",
        "emoji": "📊",
        "button": "📊 Механик"
    },
    "harmonicus": {
        "name": "📝 ГАРМОНИКУС",
        "description": "Сбалансированный журналистский стиль для статей",
        "emoji": "📝",
        "button": "📝 Гармония"
    },
    "architect": {
        "name": "✨ АРХИТЕКТОР",
        "description": "Структурированный документ с четкой иерархией",
        "emoji": "✨",
        "button": "✨ Архитектор"
    }
}

# Хранение данных
user_data_store = {}

# ==================== ФУНКЦИИ ПРЕОБРАЗОВАНИЯ ====================
def apply_phoenix(text):
    """🔥 Эмоциональный текст"""
    if not text:
        return text
    
    text = re.sub(r'\s+', ' ', text.strip())
    
    if len(text.split()) < 6:
        prefixes = ["🚀 ", "🌟 ", "✨ ", "💫 ", "⚡ "]
        result = random.choice(prefixes) + text.upper() + "!"
    else:
        sentences = re.split(r'[.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if sentences:
            sentences[0] = "🚀 " + sentences[0].capitalize()
            
            emojis = ["✨ ", "🌟 ", "💫 ", "⚡ ", "🎯 "]
            for i in range(1, len(sentences)):
                if i-1 < len(emojis):
                    sentences[i] = emojis[i-1] + sentences[i]
            
            result = ". ".join(sentences) + "."
        else:
            result = text
    
    return result

def apply_ice(text):
    """🧊 Фактологический текст"""
    if not text:
        return text
    
    emotional_words = ["очень", "крайне", "невероятно", "потрясающе", "восхитительно"]
    
    words = text.split()
    clean_words = []
    
    for word in words:
        if word.lower() not in emotional_words:
            clean_word = re.sub(r'[!?]+', '', word)
            clean_words.append(clean_word)
    
    result = " ".join(clean_words)
    result = result.replace('!', '.').replace('?', '.')
    
    sentences = re.split(r'[.]', result)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) > 1:
        numbered = []
        for i, sentence in enumerate(sentences, 1):
            if sentence:
                numbered.append(f"{i}. {sentence}")
        result = "\n".join(numbered)
    elif sentences:
        result = sentences[0] + "."
    
    return result

def apply_mechanicus(text):
    """📊 Технический документ"""
    if not text:
        return text
    
    words = text.split()
    
    result = "📋 ТЕХНИЧЕСКИЙ АНАЛИЗ\n"
    result += "══════════════════════════\n\n"
    result += "ОБЩИЕ СВЕДЕНИЯ:\n"
    result += f"• Объект анализа: {' '.join(words[:min(3, len(words))])}\n"
    result += f"• Объем данных: {len(words)} единиц\n"
    result += f"• Уникальные элементы: {len(set(w.lower() for w in words))}\n\n"
    
    result += "КЛЮЧЕВЫЕ КОМПОНЕНТЫ:\n"
    
    seen = set()
    key_words = []
    for word in words:
        if word.lower() not in seen and len(key_words) < 5:
            seen.add(word.lower())
            key_words.append(word)
    
    for i, word in enumerate(key_words, 1):
        result += f"{i}. {word.upper()}\n"
    
    return result

def apply_harmonicus(text):
    """📝 Журналистский стиль"""
    if not text:
        return text
    
    text = re.sub(r'\s+', ' ', text.strip())
    
    journalistic_starts = [
        "Как отмечают аналитики, ",
        "По имеющейся информации, ",
        "Согласно экспертным оценкам, ",
        "Как стало известно, "
    ]
    
    sentences = re.split(r'[.!?]', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if sentences:
        sentences[0] = random.choice(journalistic_starts) + sentences[0].lower()
        
        connectors = ["При этом, ", "Кроме того, ", "В свою очередь, "]
        for i in range(1, min(len(sentences), 4)):
            sentences[i] = connectors[i-1] + sentences[i].lower()
    
        result = ". ".join(sentences) + "."
    else:
        result = text
    
    return result

def apply_architect(text):
    """✨ Структурированный документ"""
    if not text:
        return text
    
    words = text.split()
    
    result = "📄 СТРУКТУРИРОВАННЫЙ ДОКУМЕНТ\n"
    result += "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"
    
    result += "1. РЕЗЮМЕ\n"
    if len(words) > 10:
        summary_words = words[:10]
        summary_text = ' '.join(summary_words)  # ИСПРАВЛЕНО: пробелы между словами
        result += f"   {summary_text}...\n\n"
    else:
        result += f"   {text}\n\n"
    
    result += "2. КЛЮЧЕВЫЕ АСПЕКТЫ\n"
    
    sections = min(3, max(1, len(words) // 5))
    for i in range(sections):
        start = i * 5
        end = min(start + 5, len(words))
        if start < len(words):
            section_text = " ".join(words[start:end])
            result += f"   • Аспект {i+1}: {section_text}\n"
    
    return result

def transform_text(text: str, style: str):
    """Главная функция преобразования текста"""
    if not text.strip():
        return "Вы отправили пустое сообщение.", ""
    
    if style == "phoenix":
        transformed = apply_phoenix(text)
        formatted = f"<b>🔥 ФЕНИКС (эмоциональный стиль)</b>\n\n{transformed}"
        return formatted, transformed
    
    elif style == "ice":
        transformed = apply_ice(text)
        formatted = f"<b>🧊 ЛЁД (фактологический стиль)</b>\n\n{transformed}"
        return formatted, transformed
    
    elif style == "mechanicus":
        transformed = apply_mechanicus(text)
        formatted = f"<b>📊 МЕХАНИКУС (технический стиль)</b>\n\n{transformed}"
        return formatted, transformed
    
    elif style == "harmonicus":
        transformed = apply_harmonicus(text)
        formatted = f"<b>📝 ГАРМОНИКУС (журналистский стиль)</b>\n\n{transformed}"
        return formatted, transformed
    
    elif style == "architect":
        transformed = apply_architect(text)
        formatted = f"<b>✨ АРХИТЕКТОР (структурированный стиль)</b>\n\n{transformed}"
        return formatted, transformed
    
    else:
        return f"<b>Оригинальный текст:</b>\n\n{text}", text

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
        [InlineKeyboardButton("❓ Помощь", callback_data="help")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_html(
        f"⚗️ <b>TextAlchemic Bot</b>\n\n"
        f"Привет, {user.mention_html()}! Выберите стиль преобразования текста:\n\n"
        f"<b>Доступные стили:</b>\n"
        f"• 🔥 ФЕНИКС — для соцсетей и рекламы\n"
        f"• 🧊 ЛЁД — для отчётов и документов\n"
        f"• 📊 МЕХАНИКУС — для технической документации\n"
        f"• 📝 ГАРМОНИКУС — для статей и публикаций\n"
        f"• ✨ АРХИТЕКТОР — для структурированных документов\n\n"
        f"<i>Нажмите на кнопку ниже, чтобы выбрать стиль.</i>",
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
            user_data_store[user_id]['current_style'] = style_key
            
            style_info = STYLES[style_key]
            
            # Проверяем, есть ли сохраненный текст
            has_previous_text = (
                user_id in user_data_store and 
                'original_text' in user_data_store[user_id] and 
                user_data_store[user_id]['original_text']
            )
            
            if has_previous_text:
                # Предлагаем выбор
                keyboard = [
                    [InlineKeyboardButton("✅ Использовать предыдущий текст", callback_data=f"use_previous_{style_key}")],
                    [InlineKeyboardButton("📝 Ввести новый текст", callback_data="enter_new_text")],
                    [InlineKeyboardButton("🔄 Выбрать другой стиль", callback_data="change_style")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                prev_text = user_data_store[user_id]['original_text']
                preview = prev_text[:50] + ("..." if len(prev_text) > 50 else "")
                
                await query.edit_message_text(
                    f"{style_info['emoji']} <b>Выбран стиль: {style_info['name']}</b>\n\n"
                    f"{style_info['description']}\n\n"
                    f"<b>У вас есть сохранённый текст:</b>\n"
                    f"«{preview}»\n\n"
                    f"<i>Использовать этот текст или ввести новый?</i>",
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
            else:
                # Нет сохранённого текста
                await query.edit_message_text(
                    f"{style_info['emoji']} <b>Выбран стиль: {style_info['name']}</b>\n\n"
                    f"{style_info['description']}\n\n"
                    f"<i>Отправьте текст для преобразования в этом стиле.</i>",
                    parse_mode='HTML'
                )
    
    elif query.data.startswith("use_previous_"):
        # Использовать предыдущий текст
        style_key = query.data.replace("use_previous_", "")
        
        if user_id in user_data_store and 'original_text' in user_data_store[user_id]:
            original_text = user_data_store[user_id]['original_text']
            
            # Преобразуем текст
            formatted_result, clean_result = transform_text(original_text, style_key)
            
            # Сохраняем результат
            user_data_store[user_id]['current_style'] = style_key
            user_data_store[user_id]['last_clean_text'] = clean_result
            user_data_store[user_id]['last_formatted_result'] = formatted_result
            
            # Показываем результат с кнопками
            await show_result_with_buttons(query.message, user_id, style_key)
    
    elif query.data == "enter_new_text":
        await query.edit_message_text(
            "📝 <b>Отправьте новый текст для преобразования:</b>\n\n"
            "<i>Просто напишите сообщение с текстом.</i>",
            parse_mode='HTML'
        )
    
    elif query.data == "change_style":
        # Показать выбор стиля
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
        await show_help(query.message)

async def show_result_with_buttons(message, user_id, style_key):
    """Показать результат с кнопками"""
    if user_id in user_data_store and 'last_formatted_result' in user_data_store[user_id]:
        # Отправляем форматированный текст
        await message.reply_text(
            user_data_store[user_id]['last_formatted_result'],
            parse_mode='HTML'
        )
        
        # Отправляем чистый текст
        await message.reply_text(
            user_data_store[user_id]['last_clean_text']
        )
        
        # Отправляем сообщение с кнопками
        style_info = STYLES[style_key]
        keyboard = [
            [
                InlineKeyboardButton("🎭 Сменить стиль", callback_data="change_style"),
                InlineKeyboardButton("🔄 Новый текст", callback_data="enter_new_text")
            ],
            [InlineKeyboardButton("❓ Помощь", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await message.reply_text(
            f"{style_info['emoji']} <b>Что дальше?</b>\n\n"
            f"• Вы можете изменить стиль для этого текста\n"
            f"• Или преобразовать новый текст\n"
            f"• Или получить помощь",
            parse_mode='HTML',
            reply_markup=reply_markup
        )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    user_id = update.effective_user.id
    
    if user_id in user_data_store and 'current_style' in user_data_store[user_id]:
        style_key = user_data_store[user_id]['current_style']
        user_text = update.message.text
        
        # Преобразуем текст
        formatted_result, clean_result = transform_text(user_text, style_key)
        
        # Сохраняем
        user_data_store[user_id]['original_text'] = user_text
        user_data_store[user_id]['last_clean_text'] = clean_result
        user_data_store[user_id]['last_formatted_result'] = formatted_result
        
        # Показываем результат с кнопками
        await show_result_with_buttons(update.message, user_id, style_key)
    else:
        # Стиль не выбран
        keyboard = [
            [InlineKeyboardButton("🎭 Выбрать стиль", callback_data="change_style")],
            [InlineKeyboardButton("❓ Помощь", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "⚠️ <b>Сначала выберите стиль преобразования!</b>\n\n"
            "Нажмите кнопку ниже, чтобы выбрать стиль.",
            parse_mode='HTML',
            reply_markup=reply_markup
        )

async def show_help(message):
    """Показать справку"""
    keyboard = [
        [InlineKeyboardButton("🎭 Выбрать стиль", callback_data="change_style")],
        [InlineKeyboardButton("🚀 Начать работу", callback_data="enter_new_text")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await message.reply_text(
        "🛠 <b>Помощь по TextAlchemic Bot:</b>\n\n"
        "1. <b>Как использовать:</b>\n"
        "   • Выберите стиль\n"
        "   • Отправьте текст\n"
        "   • Получите результат\n\n"
        "2. <b>Особенности:</b>\n"
        "   • Бот запоминает ваш текст\n"
        "   • При смене стиля предложит использовать его\n"
        "   • Копируйте второе сообщение (чистый текст)\n\n"
        "3. <b>Стили:</b>\n"
        "   • 🔥 ФЕНИКС — эмоциональный\n"
        "   • 🧊 ЛЁД — фактологический\n"
        "   • 📊 МЕХАНИКУС — технический\n"
        "   • 📝 ГАРМОНИКУС — журналистский\n"
        "   • ✨ АРХИТЕКТОР — структурированный\n\n"
        "<i>TextAlchemic — превращаем текст в нужный стиль!</i>",
        parse_mode='HTML',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    await show_help(update.message)

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
    
    application.add_handler(CallbackQueryHandler(button_handler))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    application.add_error_handler(error_handler)
    
    print("🤖 TextAlchemic запущен и готов к работе!")
    print("ℹ️  Напишите боту: /start для начала")
    application.run_polling()

if __name__ == '__main__':
    main()
