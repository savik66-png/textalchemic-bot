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

# Улучшенные стили с разнообразными эмодзи
STYLES = {
    "phoenix": {
        "name": "🔥 ФЕНИКС",
        "description": "Эмоциональный, энергичный текст с яркими образами",
        "emoji": "🔥",
        "button": "🔥 Феникс",
        "emojis": ["🚀", "💫", "🌟", "✨", "🎯", "⚡", "💥", "🌈", "🎉", "🎊"]
    },
    "ice": {
        "name": "🧊 ЛЁД",
        "description": "Фактологический, нейтральный текст без эмоций",
        "emoji": "🧊",
        "button": "🧊 Лёд",
        "emojis": ["📊", "📈", "📉", "📋", "🎯", "⚖️", "🔍", "📝", "📌", "📍"]
    },
    "mechanicus": {
        "name": "📊 МЕХАНИКУС",
        "description": "Технический документ со структурированными данными",
        "emoji": "📊",
        "button": "📊 Механик",
        "emojis": ["🔧", "⚙️", "🔩", "📐", "🧮", "💾", "🖥️", "🔌", "🔋", "🛠️"]
    },
    "harmonicus": {
        "name": "📝 ГАРМОНИКУС",
        "description": "Сбалансированный журналистский стиль для статей",
        "emoji": "📝",
        "button": "📝 Гармония",
        "emojis": ["🎵", "🎶", "🎼", "🔄", "⚖️", "🌈", "☯️", "🕊️", "🌿", "🍃"]
    },
    "architect": {
        "name": "✨ АРХИТЕКТОР",
        "description": "Структурированный документ с четкой иерархией",
        "emoji": "✨",
        "button": "✨ Архитектор",
        "emojis": ["🏛️", "🗂️", "📑", "📄", "📋", "🏗️", "🕌", "🏢", "🏭", "📐"]
    }
}

# Хранение данных пользователей
user_data_store = {}

# ==================== УЛУЧШЕННЫЕ ФУНКЦИИ ПРЕОБРАЗОВАНИЯ ====================
def apply_phoenix(text):
    """🔥 Эмоциональный, энергичный текст для соцсетей и рекламы"""
    if not text:
        return text
    
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Разнообразные эмоциональные префиксы
    emotional_prefixes = [
        "🚀 Прорыв: ", "🌟 Важное: ", "💫 Невероятно: ", 
        "✨ Исключительно: ", "🎯 Точно: ", "⚡ Мгновенно: ",
        "💥 Сенсационно: ", "🌈 Уникально: ", "🎉 Эксклюзивно: "
    ]
    
    # Эмоциональные усилители
    intensifiers = [
        "невероятно", "потрясающе", "фантастически", "восхитительно",
        "исключительно", "значительно", "качественно", "эффективно"
    ]
    
    # Живые окончания
    endings = [
        " — результат, который впечатляет!",
        " — то, что вы давно ждали!",
        " — новое слово в индустрии!",
        " — прогресс налицо!",
        " — качественный скачок вперед!"
    ]
    
    # Обрабатываем в зависимости от длины
    words = text.split()
    
    if len(words) < 8:
        # Короткий текст - делаем ярким заголовком
        result = random.choice(emotional_prefixes) + text.capitalize()
    else:
        # Длинный текст - добавляем эмоции в ключевые места
        sentences = re.split(r'[.!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if sentences:
            # Первое предложение делаем мощным
            first_words = sentences[0].split()
            if len(first_words) > 3:
                insert_pos = random.randint(1, len(first_words)-1)
                first_words.insert(insert_pos, random.choice(intensifiers))
                sentences[0] = " ".join(first_words)
            
            sentences[0] = "🚀 " + sentences[0].capitalize()
            
            # Добавляем эмодзи через предложения
            emoji_cycle = ["🌟 ", "✨ ", "💫 ", "⚡ ", "💥 "]
            for i in range(len(sentences)):
                if i < len(emoji_cycle) and i > 0:
                    sentences[i] = emoji_cycle[i] + sentences[i]
            
            result = ". ".join(sentences) + "."
        else:
            result = text
    
    # Добавляем естественное завершение
    result += random.choice(endings)
    
    return result

def apply_ice(text):
    """🧊 Фактологический, нейтральный текст для отчетов"""
    if not text:
        return text
    
    # Убираем эмоциональные слова
    emotional_words = [
        "очень", "крайне", "невероятно", "потрясающе", "восхитительно",
        "ужасно", "страшно", "прекрасно", "великолепно", "изумительно",
        "замечательно", "превосходно", "отлично", "шикарно", "роскошно"
    ]
    
    words = text.split()
    clean_words = []
    
    for word in words:
        word_lower = word.lower()
        # Убираем эмоциональные слова
        if word_lower not in emotional_words:
            # Убираем восклицательные знаки
            clean_word = re.sub(r'[!?]+', '.', word)
            clean_words.append(clean_word)
    
    result = " ".join(clean_words)
    
    # Заменяем эмоциональную пунктуацию
    result = result.replace('!', '.').replace('?', '.')
    
    # Структурируем как факты
    sentences = re.split(r'[.]', result)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) > 1:
        # Если несколько предложений - нумеруем факты
        numbered = []
        for i, sentence in enumerate(sentences, 1):
            if sentence:
                numbered.append(f"{i}. {sentence}")
        result = "\n".join(numbered)
    elif sentences:
        # Одно предложение
        result = sentences[0] + "."
    
    return result

def apply_mechanicus(text):
    """📊 Технический документ со структурированными данными"""
    if not text:
        return text
    
    words = text.split()
    
    # Создаем технический документ БЕЗ технических надписей в конце
    result = "📋 ТЕХНИЧЕСКАЯ СПЕЦИФИКАЦИЯ\n"
    result += "═══════════════════════════════════\n\n"
    
    # 1. Идентификационные данные
    result += "1. ИДЕНТИФИКАЦИЯ\n"
    result += f"   • Объект: {' '.join(words[:min(3, len(words))])}\n"
    result += f"   • Объем данных: {len(words)} лексических единиц\n"
    result += f"   • Информационная плотность: {len(set(w.lower() for w in words))}/{len(words)}\n\n"
    
    # 2. Компонентный анализ
    result += "2. КОМПОНЕНТНЫЙ АНАЛИЗ\n"
    
    # Выбираем ключевые компоненты
    unique_words = []
    for word in words:
        if word.lower() not in [w.lower() for w in unique_words] and len(unique_words) < 6:
            unique_words.append(word)
    
    for i, word in enumerate(unique_words, 1):
        result += f"   {i}. {word.upper()} — базовый компонент\n"
    
    result += "\n"
    
    # 3. Операционные характеристики
    result += "3. ОПЕРАЦИОННЫЕ ХАРАКТЕРИСТИКИ\n"
    characteristics = [
        "Структурированность представления",
        "Информационная завершенность",
        "Логическая последовательность",
        "Фактологическая точность"
    ]
    
    for char in characteristics:
        result += f"   • {char}\n"
    
    return result

def apply_harmonicus(text):
    """📝 Сбалансированный журналистский стиль для статей"""
    if not text:
        return text
    
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Разбиваем на предложения
    sentences = re.split(r'[.!?]', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return text
    
    # Журналистские приемы
    journalistic_opens = [
        "Как отмечают эксперты, ",
        "Согласно последним данным, ",
        "В ходе анализа выяснилось, что ",
        "Как стало известно, ",
        "По предварительной информации, "
    ]
    
    journalistic_connectors = [
        "При этом, ", "Кроме того, ", "Одновременно с этим, ",
        "В свою очередь, ", "Что касается ", "Если говорить о "
    ]
    
    # Первое предложение в журналистском стиле
    if len(sentences) > 0:
        sentences[0] = random.choice(journalistic_opens) + sentences[0].lower()
    
    # Добавляем журналистские связки
    for i in range(1, min(len(sentences), len(journalistic_connectors) + 1)):
        sentences[i] = journalistic_connectors[i-1] + sentences[i].lower()
    
    # Собираем текст
    result = ""
    for i, sentence in enumerate(sentences):
        if i == 0:
            result = sentence
        else:
            result += " " + sentence
    
    result = result.rstrip('. ') + '.'
    
    # Добавляем журналистское резюме для длинных текстов
    if len(sentences) > 2:
        summaries = [
            "Таковы основные аспекты рассматриваемого вопроса.",
            "Эти данные позволяют сделать определенные выводы.",
            "Подобная информация требует внимательного изучения."
        ]
        result += " " + random.choice(summaries)
    
    return result

def apply_architect(text):
    """✨ Структурированный документ с четкой иерархией"""
    if not text:
        return text
    
    words = text.split()
    
    # Создаем структурированный документ БЕЗ технических надписей
    result = "📄 СТРУКТУРИРОВАННЫЙ ДОКУМЕНТ\n"
    result += "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"
    
    # 1. Резюме
    result += "1. РЕЗЮМЕ\n"
    if len(words) > 15:
        summary_words = words[:15]
        result += f"   {''.join([w.capitalize() if i == 0 else w for i, w in enumerate(summary_words)])}...\n\n"
    else:
        result += f"   {text}\n\n"
    
    # 2. Основные положения
    result += "2. ОСНОВНЫЕ ПОЛОЖЕНИЯ\n"
    
    # Определяем количество разделов
    if len(words) < 20:
        sections = 2
    elif len(words) < 50:
        sections = 3
    else:
        sections = 4
    
    section_size = max(1, len(words) // sections)
    
    for i in range(sections):
        start = i * section_size
        end = min(start + section_size, len(words))
        
        if start < len(words):
            section_words = words[start:end]
            if section_words:
                result += f"\n   2.{i+1}. Блок {i+1}\n"
                result += f"      • Содержание: {' '.join(section_words)}\n"
    
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

# ==================== ТЕЛЕГРАМ БОТ С ИСПРАВЛЕННОЙ АРХИТЕКТУРОЙ ====================
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
    
    # Отправляем сообщение с кнопками (оно всегда будет внизу)
    message = await update.message.reply_html(
        f"⚗️ <b>TextAlchemic Bot</b>\n\n"
        f"Привет, {user.mention_html()}! Выберите стиль преобразования:\n\n"
        f"• 🔥 ФЕНИКС — эмоциональный текст для соцсетей\n"
        f"• 🧊 ЛЁД — фактологический текст для отчётов\n"
        f"• 📊 МЕХАНИКУС — технический документ\n"
        f"• 📝 ГАРМОНИКУС — журналистский стиль для статей\n"
        f"• ✨ АРХИТЕКТОР — структурированный документ\n\n"
        f"<i>Нажмите на кнопку, чтобы выбрать стиль.</i>",
        reply_markup=reply_markup
    )
    
    # Сохраняем ID сообщения с кнопками
    user_id = update.effective_user.id
    if user_id not in user_data_store:
        user_data_store[user_id] = {}
    user_data_store[user_id]['buttons_message_id'] = message.message_id

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if query.data.startswith("style_"):
        style_key = query.data.replace("style_", "")
        
        if style_key in STYLES:
            style_info = STYLES[style_key]
            
            # Сохраняем выбранный стиль
            if user_id not in user_data_store:
                user_data_store[user_id] = {}
            user_data_store[user_id]['current_style'] = style_key
            
            # Проверяем, есть ли сохраненный текст
            has_previous_text = (
                user_id in user_data_store and 
                'original_text' in user_data_store[user_id] and 
                user_data_store[user_id]['original_text']
            )
            
            if has_previous_text:
                # Предлагаем выбор: использовать старый текст или новый
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
            await show_result(query.message, user_id, style_key)
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

async def show_result(message, user_id, style_key):
    """Показать результат преобразования"""
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
        
        # Обновляем сообщение с кнопками (всегда внизу)
        style_info = STYLES[style_key]
        keyboard = [
            [
                InlineKeyboardButton("🎭 Сменить стиль", callback_data="change_style"),
                InlineKeyboardButton("🔄 Новый текст", callback_data="send_text")
            ],
            [InlineKeyboardButton("❓ Помощь", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Редактируем сообщение с кнопками
        if 'buttons_message_id' in user_data_store[user_id]:
            try:
                await message.bot.edit_message_text(
                    chat_id=message.chat_id,
                    message_id=user_data_store[user_id]['buttons_message_id'],
                    text=f"{style_info['emoji']} <b>Текст преобразован в стиле {style_info['name']}</b>\n\n"
                         f"<i>Выше вы видите результат. Вы можете:</i>\n"
                         f"• Сменить стиль для этого текста\n"
                         f"• Преобразовать новый текст\n"
                         f"• Получить помощь по работе с ботом",
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
            except Exception as e:
                logger.error(f"Ошибка при редактировании сообщения: {e}")
                # Если не удалось отредактировать, отправляем новое сообщение с кнопками
                new_message = await message.reply_text(
                    f"{style_info['emoji']} <b>Текст преобразован в стиле {style_info['name']}</b>\n\n"
                    f"<i>Выше вы видите результат. Вы можете:</i>\n"
                    f"• Сменить стиль для этого текста\n"
                    f"• Преобразовать новый текст\n"
                    f"• Получить помощь по работе с ботом",
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
                user_data_store[user_id]['buttons_message_id'] = new_message.message_id

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
        "     - Первое: текст с форматированием\n"
        "     - Второе: чистый текст для копирования\n\n"
        "2. <b>Особенности:</b>\n"
        "   • Бот запоминает ваш последний текст\n"
        "   • При смене стиля предложит использовать его\n"
        "   • Для копирования используйте второе сообщение\n\n"
        "3. <b>Стили:</b>\n"
        "   • 🔥 ФЕНИКС — эмоциональный текст с эмодзи\n"
        "   • 🧊 ЛЁД — факты без эмоций\n"
        "   • 📊 МЕХАНИКУС — технический документ\n"
        "   • 📝 ГАРМОНИКУС — журналистский стиль\n"
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
        await show_result(update.message, user_id, style_key)
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
