import os
import logging
import re
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")

# Стили с улучшенными описаниями
STYLES = {
    "phoenix": {
        "name": "🔥 ФЕНИКС",
        "description": "Добавляет эмоции, энергию, делает текст живым и ярким",
        "emoji": "🔥",
        "button": "🔥 Феникс",
        "emojis": ["🚀", "💥", "🌟", "✨", "🎯", "💫", "⚡"]
    },
    "ice": {
        "name": "🧊 ЛЁД",
        "description": "Убирает эмоции, оставляет только факты и цифры",
        "emoji": "🧊",
        "button": "🧊 Лёд",
        "emojis": ["📊", "📈", "📉", "📋", "🎯", "⚖️", "🔍"]
    },
    "mechanicus": {
        "name": "📊 МЕХАНИКУС",
        "description": "Структурирует текст как техническую документацию",
        "emoji": "📊",
        "button": "📊 Механик",
        "emojis": ["🔧", "⚙️", "🔩", "📐", "🧮", "💾", "🖥️"]
    },
    "harmonicus": {
        "name": "📝 ГАРМОНИКУС",
        "description": "Балансирует текст, делает его плавным и читаемым",
        "emoji": "📝",
        "button": "📝 Гармония",
        "emojis": ["🎵", "🎶", "🎼", "🔄", "⚖️", "🌈", "☯️"]
    },
    "architect": {
        "name": "✨ АРХИТЕКТОР",
        "description": "Создаёт чёткую структуру с заголовками и разделами",
        "emoji": "✨",
        "button": "✨ Архитектор",
        "emojis": ["🏛️", "🗂️", "📑", "📄", "📋", "🏗️", "🕌"]
    }
}

# Хранение данных пользователей в памяти (временное решение)
user_data_store = {}

# ==================== УЛУЧШЕННЫЕ ФУНКЦИИ ПРЕОБРАЗОВАНИЯ ====================
def apply_phoenix(text):
    """🔥 Делает текст эмоциональным и энергичным"""
    if not text:
        return text
    
    # Убираем лишние пробелы
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Разные стратегии для разной длины текста
    if len(text.split()) < 5:
        # Короткий текст - добавляем энергию
        emotional_prefixes = [
            "🔥 ВАЖНО: ", "🚀 УЛЕТ: ", "💥 ВНИМАНИЕ: ", 
            "🌟 ОГО: ", "✨ ВАУ: ", "🎯 ТОЧНО: "
        ]
        result = random.choice(emotional_prefixes) + text.upper() + "!"
    else:
        # Длинный текст - добавляем эмоциональные вставки
        sentences = re.split(r'[.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if sentences:
            # Делаем первое предложение ярким
            sentences[0] = "🔥 " + sentences[0].capitalize()
            
            # Добавляем эмодзи через каждые 2-3 предложения
            for i in range(2, len(sentences), 3):
                if i < len(sentences):
                    sentences[i] = random.choice(["✨ ", "🚀 ", "💫 "]) + sentences[i]
            
            result = ". ".join(sentences) + "."
        else:
            result = text
    
    # Добавляем эмоциональное завершение
    endings = [
        " 🔥 Вот это да!", 
        " 🚀 Просто космос!", 
        " 💥 Зажигательно!",
        " 🌟 Блестяще!",
        " ✨ Волшебно!"
    ]
    result += random.choice(endings)
    
    return result

def apply_ice(text):
    """🧊 Делает текст фактологическим и холодным"""
    if not text:
        return text
    
    # Убираем эмоциональные слова
    emotional_words = [
        "очень", "крайне", "невероятно", "потрясающе", "восхитительно",
        "ужасно", "страшно", "прекрасно", "великолепно", "изумительно",
        "замечательно", "превосходно", "отлично"
    ]
    
    words = text.split()
    clean_words = []
    
    for word in words:
        # Приводим к нижнему регистру для сравнения
        word_lower = word.lower()
        # Убираем эмоциональные слова
        if word_lower not in emotional_words:
            # Убираем восклицательные и вопросительные знаки
            clean_word = re.sub(r'[!?]+', '', word)
            clean_words.append(clean_word)
    
    # Собираем текст
    result = " ".join(clean_words)
    
    # Заменяем точки на нейтральные разделители
    result = result.replace('!', '.').replace('?', '.')
    
    # Делаем текст более структурированным
    sentences = re.split(r'[.]', result)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if sentences:
        # Нумеруем факты, если их несколько
        if len(sentences) > 1:
            numbered_sentences = []
            for i, sentence in enumerate(sentences, 1):
                numbered_sentences.append(f"{i}. {sentence}.")
            result = "\n".join(numbered_sentences)
        else:
            result = sentences[0] + "."
    else:
        result = text
    
    # Добавляем нейтральное завершение
    result += " 📊 Данные приведены к фактологическому виду."
    
    return result

def apply_mechanicus(text):
    """📊 Преобразует текст в техническую документацию"""
    if not text:
        return text
    
    words = text.split()
    
    # Создаем структурированный документ
    result = "📋 ТЕХНИЧЕСКОЕ ЗАДАНИЕ\n"
    result += "═" * 35 + "\n\n"
    
    # 1. Общие сведения
    result += "1. ОБЩИЕ СВЕДЕНИЯ\n"
    result += f"   • Тема: {' '.join(words[:min(3, len(words))])}\n"
    result += f"   • Объём: {len(words)} слов, {len(text)} символов\n"
    result += f"   • Уникальных слов: {len(set([w.lower() for w in words]))}\n\n"
    
    # 2. Основные компоненты
    result += "2. ОСНОВНЫЕ КОМПОНЕНТЫ\n"
    
    # Берем ключевые слова (первые 5 уникальных слов)
    seen_words = set()
    key_words = []
    for word in words:
        if word.lower() not in seen_words and len(seen_words) < 5:
            seen_words.add(word.lower())
            key_words.append(word)
    
    for i, word in enumerate(key_words, 1):
        result += f"   {i}. {word.upper()} — ключевой элемент\n"
    
    result += "\n"
    
    # 3. Требования
    result += "3. ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ\n"
    requirements = [
        "Структурированность информации",
        "Чёткость формулировок",
        "Отсутствие эмоциональной окраски",
        "Логическая последовательность"
    ]
    
    for req in requirements:
        result += f"   • {req}\n"
    
    result += "\n" + "═" * 35
    result += "\n✅ Документ структурирован по техническим стандартам."
    
    return result

def apply_harmonicus(text):
    """📝 Балансирует текст для лучшего чтения"""
    if not text:
        return text
    
    # Нормализуем пробелы
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Разбиваем на предложения
    sentences = re.split(r'[.!?]', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return text
    
    # Балансируем длину предложений
    balanced = []
    for sentence in sentences:
        words = sentence.split()
        
        if len(words) > 20:
            # Слишком длинное - разбиваем
            parts = []
            current_part = []
            current_length = 0
            
            for word in words:
                current_part.append(word)
                current_length += len(word) + 1
                
                if current_length > 15 and len(current_part) > 1:
                    parts.append(" ".join(current_part))
                    current_part = []
                    current_length = 0
            
            if current_part:
                parts.append(" ".join(current_part))
            
            balanced.extend(parts)
        elif len(words) < 3:
            # Слишком короткое - объединяем со следующим или добавляем контекст
            balanced.append(sentence + " (важный аспект)")
        else:
            balanced.append(sentence)
    
    # Соединяем с плавными переходами
    if len(balanced) == 1:
        result = balanced[0].capitalize() + "."
    else:
        connectors = [
            "В частности, ", "Кроме того, ", "При этом ", 
            "Таким образом, ", "Следовательно, ", "Однако "
        ]
        
        result = balanced[0].capitalize()
        for i in range(1, len(balanced)):
            if i <= len(connectors):
                result += ". " + connectors[i-1] + balanced[i].lower()
            else:
                result += ". " + balanced[i].capitalize()
        
        result += "."
    
    return result

def apply_architect(text):
    """✨ Создаёт структурированный документ"""
    if not text:
        return text
    
    words = text.split()
    
    # Создаём документ с чёткой структурой
    result = "🏛️ СТРУКТУРИРОВАННЫЙ ДОКУМЕНТ\n"
    result += "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"
    
    # 1. Резюме
    result += "📌 РЕЗЮМЕ\n"
    if len(words) > 10:
        summary_words = words[:10]
        result += f"Основная тема: {' '.join(summary_words)}...\n\n"
    else:
        result += f"Содержание: {text}\n\n"
    
    # 2. Ключевые разделы
    result += "🗂️ КЛЮЧЕВЫЕ РАЗДЕЛЫ\n"
    
    # Определяем количество разделов на основе длины текста
    if len(words) < 10:
        sections = 2
    elif len(words) < 30:
        sections = 3
    else:
        sections = 4
    
    section_size = len(words) // sections
    
    for i in range(sections):
        start = i * section_size
        end = min(start + min(section_size, 15), len(words))
        
        if start < len(words):
            section_words = words[start:end]
            if section_words:
                result += f"\n{i+1}. РАЗДЕЛ {i+1}\n"
                result += f"   • Содержание: {' '.join(section_words)}\n"
                result += f"   • Объём: {len(section_words)} слов\n"
    
    result += "\n▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
    result += "✅ Документ структурирован и готов к использованию."
    
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
        transformed = apply_phoenix(text)  # Временно используем phoenix
        formatted = f"<b>📝 ГАРМОНИКУС (сбалансированный стиль)</b>\n\n{transformed}"
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
        f"Привет, {user.mention_html()}! Я помогу преобразовать ваш текст в нужный стиль.\n\n"
        f"<b>Выберите стиль:</b>\n"
        f"• 🔥 ФЕНИКС — для ярких, эмоциональных текстов\n"
        f"• 🧊 ЛЁД — для фактологических и нейтральных текстов\n"
        f"• 📊 МЕХАНИКУС — для технических документов\n"
        f"• 📝 ГАРМОНИКУС — для сбалансированных текстов\n"
        f"• ✨ АРХИТЕКТОР — для структурированных документов\n\n"
        f"<i>После выбора стиля отправьте текст для преобразования.</i>",
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
            # Сохраняем выбранный стиль
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
                # Предлагаем выбор: использовать старый текст или ввести новый
                keyboard = [
                    [InlineKeyboardButton("✅ Использовать предыдущий текст", callback_data=f"use_previous_{style_key}")],
                    [InlineKeyboardButton("📝 Ввести новый текст", callback_data="enter_new_text")],
                    [InlineKeyboardButton("🔄 Выбрать другой стиль", callback_data="change_style")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                # Показываем начало предыдущего текста
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
                # Нет сохранённого текста - просим ввести
                keyboard = [
                    [InlineKeyboardButton("📝 Отправить текст", callback_data="send_text")],
                    [InlineKeyboardButton("🔄 Выбрать другой стиль", callback_data="change_style")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    f"{style_info['emoji']} <b>Выбран стиль: {style_info['name']}</b>\n\n"
                    f"{style_info['description']}\n\n"
                    f"<i>Нажмите «Отправить текст» и напишите текст для преобразования.</i>",
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
    
    elif query.data.startswith("use_previous_"):
        # Использовать предыдущий текст с новым стилем
        style_key = query.data.replace("use_previous_", "")
        
        if user_id in user_data_store and 'original_text' in user_data_store[user_id]:
            original_text = user_data_store[user_id]['original_text']
            
            # Преобразуем текст
            formatted_result, clean_result = transform_text(original_text, style_key)
            
            # Сохраняем результат
            user_data_store[user_id]['current_style'] = style_key
            user_data_store[user_id]['last_clean_text'] = clean_result
            user_data_store[user_id]['last_formatted_result'] = formatted_result
            
            # Показываем результат
            await show_result(query.message, user_id)
        else:
            await query.edit_message_text(
                "⚠️ <b>Не найден сохранённый текст</b>\n\n"
                "Нажмите «Ввести новый текст».",
                parse_mode='HTML'
            )
    
    elif query.data == "enter_new_text":
        # Запрос нового текста
        await query.edit_message_text(
            "📝 <b>Отправьте новый текст для преобразования:</b>\n\n"
            "<i>Просто напишите сообщение с текстом, который нужно преобразовать.</i>",
            parse_mode='HTML'
        )
    
    elif query.data == "send_text":
        await query.edit_message_text(
            "📝 <b>Отправьте текст для преобразования:</b>\n\n"
            "<i>Напишите сообщение с текстом, который нужно преобразовать.</i>",
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
        await show_help(query.message)

async def show_result(message, user_id):
    """Показать результат преобразования"""
    if user_id in user_data_store and 'last_formatted_result' in user_data_store[user_id]:
        # Кнопки для управления
        keyboard = [
            [
                InlineKeyboardButton("🎭 Сменить стиль", callback_data="change_style"),
                InlineKeyboardButton("🔄 Новый текст", callback_data="send_text")
            ],
            [InlineKeyboardButton("❓ Помощь", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Отправляем информационное сообщение
        await message.reply_text(
            user_data_store[user_id]['last_formatted_result'],
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        
        # Отправляем чистый текст для копирования
        await message.reply_text(
            user_data_store[user_id]['last_clean_text']
        )

async def show_help(message):
    """Показать справку"""
    keyboard = [
        [InlineKeyboardButton("🎭 Выбрать стиль", callback_data="change_style")],
        [InlineKeyboardButton("🚀 Начать работу", callback_data="send_text")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await message.reply_text(
        "🛠 <b>Помощь по TextAlchemic Bot:</b>\n\n"
        "1. <b>Как использовать:</b>\n"
        "   • Выберите стиль преобразования\n"
        "   • Отправьте текст\n"
        "   • Получите два сообщения:\n"
        "     - Первое: информация о стиле\n"
        "     - Второе: чистый текст для копирования\n\n"
        "2. <b>Особенности:</b>\n"
        "   • Бот запоминает ваш последний текст\n"
        "   • При смене стиля предложит использовать его\n"
        "   • Для копирования используйте второе сообщение\n\n"
        "3. <b>Стили:</b>\n"
        "   • 🔥 ФЕНИКС — эмоциональный текст с эмодзи\n"
        "   • 🧊 ЛЁД — факты без эмоций\n"
        "   • 📊 МЕХАНИКУС — технический документ\n"
        "   • 📝 ГАРМОНИКУС — сбалансированный текст\n"
        "   • ✨ АРХИТЕКТОР — структурированный документ\n\n"
        "<i>TextAlchemic — превращаем текст в нужный стиль!</i>",
        parse_mode='HTML',
        reply_markup=reply_markup
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    user_id = update.effective_user.id
    
    # Проверяем, выбран ли стиль
    if user_id in user_data_store and 'current_style' in user_data_store[user_id]:
        style_key = user_data_store[user_id]['current_style']
        user_text = update.message.text
        
        # Преобразуем текст
        formatted_result, clean_result = transform_text(user_text, style_key)
        
        # Сохраняем всё
        user_data_store[user_id]['original_text'] = user_text
        user_data_store[user_id]['last_clean_text'] = clean_result
        user_data_store[user_id]['last_formatted_result'] = formatted_result
        
        # Показываем результат
        await show_result(update.message, user_id)
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
    
    # Создаем приложение
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Регистрируем обработчик кнопок
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Регистрируем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    print("🤖 TextAlchemic запущен и готов к работе!")
    print("ℹ️  Напишите боту: /start для начала")
    application.run_polling()

if __name__ == '__main__':
    main()
