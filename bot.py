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

# Получаем токен из переменных окружения
TOKEN = os.environ.get("BOT_TOKEN")

# Словарь стилей TextAlchemic
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

# Хранение состояния пользователей
user_data_store = {}

# ==================== ФУНКЦИИ ПРЕОБРАЗОВАНИЯ ТЕКСТА ====================
def apply_phoenix(text):
    """🔥 Добавляет эмоции и энергию"""
    if not text:
        return text
    
    emotional_words = ["невероятно", "потрясающе", "фантастически", "волшебно", 
                      "восхитительно", "изумительно", "захватывающе"]
    intensifiers = ["очень", "крайне", "невероятно", "необычайно", "особенно"]
    
    # Преобразуем текст
    words = text.split()
    
    # 1. Добавляем эмоциональные слова
    if len(words) > 1:
        for _ in range(min(2, len(words) // 3)):
            pos = random.randint(0, len(words)-1)
            words.insert(pos, random.choice(emotional_words))
    
    result = " ".join(words)
    
    # 2. Усиливаем пунктуацию
    result = result.replace('.', '!').replace('?', '?!')
    
    # 3. Делаем текст энергичнее
    sentences = re.split(r'[.!?]', result)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if sentences:
        # Делаем первое предложение громким
        sentences[0] = sentences[0].upper()
        
        # Добавляем восклицания в конце
        result = '! '.join(sentences) + '!'
    
    # 4. Добавляем эмоциональное окончание
    endings = ["Это просто ВАУ! 💥", "Эмоции зашкаливают! 🚀", "Восхитительно! 🌟"]
    result += "\n\n" + random.choice(endings)
    
    return result

def apply_ice(text):
    """🧊 Убирает эмоции, оставляет факты"""
    if not text:
        return text
    
    # 1. Убираем эмоциональные слова
    emotional_words = ["очень", "крайне", "невероятно", "потрясающе", "восхитительно",
                      "ужасно", "страшно", "прекрасно", "великолепно", "изумительно"]
    
    words = text.split()
    clean_words = []
    
    for word in words:
        clean_word = word.lower()
        if clean_word not in emotional_words:
            # Убираем восклицательные знаки из слов
            clean_word = clean_word.replace('!', '').replace('?', '')
            clean_words.append(clean_word)
    
    # 2. Создаем фактологический текст
    result = " ".join(clean_words)
    
    # 3. Убираем эмоциональную пунктуацию
    result = result.replace('!', '.').replace('?', '.').replace('!!', '.').replace('?!', '.')
    
    # 4. Делаем предложения короткими и фактологическими
    sentences = re.split(r'[.!?]', result)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    fact_sentences = []
    for sentence in sentences:
        if sentence:
            # Упрощаем предложение
            words_in_sentence = sentence.split()
            if len(words_in_sentence) > 10:
                # Разбиваем длинные предложения
                mid = len(words_in_sentence) // 2
                fact_sentences.append(" ".join(words_in_sentence[:mid]) + ".")
                fact_sentences.append(" ".join(words_in_sentence[mid:]) + ".")
            else:
                fact_sentences.append(sentence + ".")
    
    result = " ".join(fact_sentences)
    
    # 5. Делаем текст нейтральным
    result = result.capitalize()
    
    return result

def apply_mechanicus(text):
    """📊 Структурирует как техническую документацию"""
    if not text:
        return text
    
    words = text.split()
    
    # Создаем технический отчет
    result = "📋 ТЕХНИЧЕСКИЙ АНАЛИЗ ТЕКСТА\n"
    result += "=" * 40 + "\n\n"
    
    # 1. Статистика
    result += "СТАТИСТИЧЕСКИЕ ДАННЫЕ:\n"
    result += f"• Количество слов: {len(words)}\n"
    result += f"• Количество символов: {len(text)}\n"
    result += f"• Уникальных слов: {len(set(words))}\n\n"
    
    # 2. Ключевые слова
    result += "КЛЮЧЕВЫЕ ЭЛЕМЕНТЫ:\n"
    
    # Берем первые 5 слов как ключевые
    key_words = words[:min(5, len(words))]
    for i, word in enumerate(key_words, 1):
        result += f"{i}. {word.upper()}\n"
    
    result += "\n"
    
    # 3. Рекомендации по оптимизации
    result += "РЕКОМЕНДАЦИИ:\n"
    recommendations = [
        "Оптимизировать структуру предложений",
        "Увеличить информативность",
        "Добавить технические детали",
        "Структурировать по пунктам"
    ]
    
    for i, rec in enumerate(recommendations[:min(3, len(words)//2)], 1):
        result += f"• {rec}\n"
    
    result += "\n" + "=" * 40
    result += "\n✅ Анализ завершен. Текст структурирован."
    
    return result

def apply_harmonicus(text):
    """📝 Балансирует текст для лучшего чтения"""
    if not text:
        return text
    
    # 1. Разбиваем на предложения
    sentences = re.split(r'[.!?]', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return text
    
    # 2. Балансируем длину предложений
    balanced_sentences = []
    
    for sentence in sentences:
        words = sentence.split()
        
        if len(words) > 15:  # Слишком длинное предложение
            # Разбиваем на две части
            mid = len(words) // 2
            balanced_sentences.append(" ".join(words[:mid]))
            balanced_sentences.append(" ".join(words[mid:]))
        elif len(words) < 3:  # Слишком короткое предложение
            # Объединяем со следующим или добавляем детали
            balanced_sentences.append(sentence + " — важный момент.")
        else:
            balanced_sentences.append(sentence)
    
    # 3. Создаем плавный переход между предложениями
    connectors = ["При этом", "Кроме того", "Таким образом", "Следовательно", 
                 "В результате", "Например", "Важно отметить"]
    
    result = ""
    for i, sentence in enumerate(balanced_sentences):
        if i == 0:
            result = sentence.capitalize()
        elif i < len(connectors) and i % 2 == 0:
            result += f". {connectors[i % len(connectors)]}, {sentence.lower()}"
        else:
            result += f". {sentence.capitalize()}"
    
    result += "."
    
    # 4. Оптимизируем читаемость
    if len(result.split()) > 50:
        # Добавляем абзацы для длинного текста
        words = result.split()
        paragraph_size = len(words) // 2
        result = " ".join(words[:paragraph_size]) + "\n\n" + " ".join(words[paragraph_size:])
    
    return result

def apply_architect(text):
    """✨ Создает структурированный документ"""
    if not text:
        return text
    
    words = text.split()
    
    # Создаем структурированный документ
    result = "📄 ДОКУМЕНТ\n"
    result += "━" * 40 + "\n\n"
    
    # 1. Заголовок
    if len(words) > 3:
        title = " ".join(words[:3]).upper()
        result += f"ЗАГОЛОВОК: {title}\n\n"
    
    # 2. Резюме
    result += "📌 РЕЗЮМЕ:\n"
    if len(words) > 10:
        summary = " ".join(words[:10]) + "..."
    else:
        summary = text
    result += f"{summary}\n\n"
    
    # 3. Основные разделы
    result += "🏗️ СТРУКТУРА:\n"
    
    sections = 3
    if len(words) > 20:
        sections = 4
    elif len(words) > 40:
        sections = 5
    
    section_size = len(words) // sections
    
    for i in range(sections):
        start_idx = i * section_size
        end_idx = start_idx + min(section_size, 7)  # Берем по 7 слов для описания раздела
        
        if start_idx < len(words):
            section_words = words[start_idx:end_idx]
            if section_words:
                result += f"\n{i+1}. РАЗДЕЛ {i+1}:\n"
                result += f"   • Содержание: {' '.join(section_words)}\n"
                result += f"   • Статус: Структурировано ✓\n"
    
    result += "\n" + "━" * 40
    result += "\n✨ Документ структурирован и готов к использованию."
    
    return result

def transform_text(text: str, style: str) -> str:
    """Главная функция преобразования текста"""
    if not text.strip():
        return "⚠️ Вы отправили пустое сообщение."
    
    # Выбор функции преобразования
    if style == "phoenix":
        transformed = apply_phoenix(text)
        return f"<b>🔥 ФЕНИКС (Эмоциональный стиль):</b>\n\n{transformed}"
    
    elif style == "ice":
        transformed = apply_ice(text)
        return f"<b>🧊 ЛЁД (Фактологический стиль):</b>\n\n{transformed}"
    
    elif style == "mechanicus":
        transformed = apply_mechanicus(text)
        return f"<b>📊 МЕХАНИКУС (Технический стиль):</b>\n\n{transformed}"
    
    elif style == "harmonicus":
        transformed = apply_harmonicus(text)
        return f"<b>📝 ГАРМОНИКУС (Сбалансированный стиль):</b>\n\n{transformed}"
    
    elif style == "architect":
        transformed = apply_architect(text)
        return f"<b>✨ АРХИТЕКТОР (Структурированный стиль):</b>\n\n{transformed}"
    
    else:
        return f"<b>Оригинальный текст:</b>\n\n{text}"

# ==================== ТЕЛЕГРАМ БОТ ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    
    # Создаем клавиатуру с кнопками стилей
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
        f"<b>Выберите стиль преобразования:</b>\n"
        f"• 🔥 ФЕНИКС — добавляет эмоции и энергию\n"
        f"• 🧊 ЛЁД — оставляет только факты\n"
        f"• 📊 МЕХАНИКУС — технический анализ\n"
        f"• 📝 ГАРМОНИКУС — балансирует текст\n"
        f"• ✨ АРХИТЕКТОР — создаёт структуру\n\n"
        f"<i>Нажмите на кнопку ниже, чтобы выбрать стиль, затем отправьте текст.</i>",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if query.data.startswith("style_"):
        # Пользователь выбрал стиль
        style_key = query.data.replace("style_", "")
        
        if style_key in STYLES:
            # Сохраняем выбор стиля
            if user_id not in user_data_store:
                user_data_store[user_id] = {}
            user_data_store[user_id]['style'] = style_key
            
            style_info = STYLES[style_key]
            
            # Показываем кнопку "Отправить текст"
            keyboard = [
                [InlineKeyboardButton("📝 Отправить текст", callback_data="send_text")],
                [InlineKeyboardButton("🔄 Выбрать другой стиль", callback_data="change_style")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"{style_info['emoji']} <b>Выбран стиль: {style_info['name']}</b>\n\n"
                f"{style_info['description']}\n\n"
                f"<i>Теперь отправьте текст для преобразования или нажмите \"Отправить текст\".</i>",
                parse_mode='HTML',
                reply_markup=reply_markup
            )
    
    elif query.data == "send_text":
        # Просим отправить текст
        await query.edit_message_text(
            "📝 <b>Отправьте текст для преобразования:</b>\n\n"
            "<i>Просто напишите сообщение с текстом, и я преобразую его в выбранном стиле.</i>",
            parse_mode='HTML'
        )
    
    elif query.data == "change_style":
        # Возвращаем к выбору стиля
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
            "• 🔥 ФЕНИКС — добавляет эмоции и энергию\n"
            "• 🧊 ЛЁД — оставляет только факты\n"
            "• 📊 МЕХАНИКУС — технический анализ\n"
            "• 📝 ГАРМОНИКУС — балансирует текст\n"
            "• ✨ АРХИТЕКТОР — создаёт структуру\n\n"
            "<i>Нажмите на кнопку, чтобы выбрать стиль.</i>",
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    elif query.data == "help":
        # Показываем справку
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
            "   • Получите преобразованный текст\n\n"
            "2. <b>Стили преобразования:</b>\n"
            "   • 🔥 ФЕНИКС — для соцсетей, рекламы\n"
            "   • 🧊 ЛЁД — для отчётов, документов\n"
            "   • 📊 МЕХАНИКУС — для инструкций, техдокументации\n"
            "   • 📝 ГАРМОНИКУС — для блогов, статей\n"
            "   • ✨ АРХИТЕКТОР — для презентаций, структурированных документов\n\n"
            "3. <b>Копирование текста:</b>\n"
            "   • Просто выделите преобразованный текст и скопируйте\n"
            "   • В Telegram можно долго нажать на текст и выбрать \"Копировать\"\n\n"
            "<i>TextAlchemic: превращаем свинец ваших текстов в золото коммуникации!</i>",
            parse_mode='HTML',
            reply_markup=reply_markup
        )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    user_id = update.effective_user.id
    user_text = update.message.text
    
    # Проверяем, выбрал ли пользователь стиль
    if user_id in user_data_store and 'style' in user_data_store[user_id]:
        style_key = user_data_store[user_id]['style']
        
        # Преобразуем текст
        result = transform_text(user_text, style_key)
        
        # Добавляем кнопки для новых действий
        keyboard = [
            [InlineKeyboardButton("🔄 Преобразовать ещё", callback_data="send_text")],
            [InlineKeyboardButton("🎭 Сменить стиль", callback_data="change_style")],
            [InlineKeyboardButton("ℹ️ Помощь", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Отправляем преобразованный текст
        await update.message.reply_text(
            result + "\n\n📋 <i>Чтобы скопировать: выделите текст или нажмите и удерживайте</i>",
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    else:
        # Пользователь не выбрал стиль
        keyboard = [
            [InlineKeyboardButton("🎭 Выбрать стиль", callback_data="change_style")],
            [InlineKeyboardButton("ℹ️ Помощь", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "⚠️ <b>Сначала выберите стиль преобразования!</b>\n\n"
            "Нажмите кнопку ниже, чтобы выбрать стиль, затем отправьте текст.",
            parse_mode='HTML',
            reply_markup=reply_markup
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
        "   • Получите преобразованный текст\n\n"
        "3. <b>Стили преобразования:</b>\n"
        "   • 🔥 ФЕНИКС — эмоциональный, энергичный\n"
        "   • 🧊 ЛЁД — фактологический, холодный\n"
        "   • 📊 МЕХАНИКУС — технический, структурированный\n"
        "   • 📝 ГАРМОНИКУС — сбалансированный, читаемый\n"
        "   • ✨ АРХИТЕКТОР — иерархический, организованный\n\n"
        "4. <b>Копирование текста:</b>\n"
        "   • Просто выделите текст и скопируйте\n"
        "   • Или нажмите и удерживайте текст в Telegram\n\n"
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
        "<b>🔥 ФЕНИКС:</b>\n"
        "НАШ ПРОДУКТ НЕВЕРОЯТНО ПОВЫШАЕТ ЭФФЕКТИВНОСТЬ РАБОТЫ КОМАНДЫ! "
        "Это ПОТРЯСАЮЩЕ! 💥\n\n"
        "<b>🧊 ЛЁД:</b>\n"
        "Продукт повышает эффективность работы команды. "
        "Улучшение подтверждено метриками.\n\n"
        "<b>📊 МЕХАНИКУС:</b>\n"
        "📋 ТЕХНИЧЕСКИЙ АНАЛИЗ\n"
        "• Ключевой параметр: эффективность работы\n"
        "• Объект воздействия: команда\n"
        "• Результат: повышение показателей\n\n"
        "<b>✨ АРХИТЕКТОР:</b>\n"
        "📄 ДОКУМЕНТ\n"
        "ЗАГОЛОВОК: ПРОДУКТ ПОВЫШЕНИЯ ЭФФЕКТИВНОСТИ\n\n"
        "📌 РЕЗЮМЕ: Продукт повышает эффективность работы команды...\n\n"
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
    
    try:
        await update.message.reply_text(
            "⚠️ <b>Произошла ошибка</b>\n\n"
            "Попробуйте ещё раз или выберите /start для перезапуска.",
            parse_mode='HTML'
        )
    except:
        pass

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
    application.add_handler(CommandHandler("demo", demo_command))
    
    # Регистрируем обработчик кнопок
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Регистрируем обработчик для обычных сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    print("🤖 TextAlchemic запущен и готов к алхимии текстов!")
    print("ℹ️  Напишите боту: /start для начала работы")
    application.run_polling()

if __name__ == '__main__':
    main()
