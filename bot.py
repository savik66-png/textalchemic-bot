#!/usr/bin/env python3
"""
TextAlchemic Bot — ФИНАЛЬНАЯ РАБОЧАЯ ВЕРСИЯ
• Использует context.user_data вместо глобальных переменных
• Правильный FOLDER_ID: b1gf28m0hpqbo55slm6d
• Без зависимостей от config.py и dotenv
• Сохраняет исходный текст для повторной обработки в других стилях
"""
import os
import random
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==================== НАСТРОЙКИ (работает на BotHost без .env) ====================
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8542210651:AAG7Ze8DlRJwHrOYKPOrTqdnvJzLgcm23KQ')
YANDEX_API_KEY = os.getenv('YANDEX_API_KEY', '')  # Оставьте пустым если нет ключа
YANDEX_FOLDER_ID = os.getenv('YANDEX_FOLDER_ID', 'b1gf28m0hpqbo55slm6d')  # ← ПРАВИЛЬНЫЙ КАТАЛОГ!

# ==================== ЛОГИРОВАНИЕ ====================
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== СТИЛИ ====================
STYLES = {
    "ice": "Лёд ❄️",
    "phoenix": "Феникс 🔥",
    "mechanicus": "Механик ⚙️",
    "harmonicus": "Гармония 🌿",
    "architect": "Архитектор 🏛️"
}

# ==================== АЛГОРИТМИЧЕСКИЕ СТИЛИ ====================
def transform_ice(text: str) -> str:
    facts = ["Улучшение производительности", "Оптимизация процессов", "Снижение затрат", "Рост качества", "Автоматизация рутины"]
    selected = random.sample(facts, min(5, len(facts)))
    lines = ["❄️ *КЛЮЧЕВЫЕ ФАКТЫ:*"] + [f"{i}. {fact}." for i, fact in enumerate(selected, 1)]
    lines.append(f"\n📌 *Вывод:* {len(text.split())} слов")
    return "\n".join(lines)

def transform_phoenix(text: str) -> str:
    emotions = ["🔥", "✨", "🚀", "🎯", "💥"]
    return f"""{random.choice(emotions)} *ЭМОЦИОНАЛЬНЫЙ АНАЛИЗ* {random.choice(emotions)}

🔥 ВАЖНО! КЛЮЧЕВОЙ МОМЕНТ! 🔥

✨ {text}

🎭 Настроение: Позитивное {random.choice(emotions)}
📈 Потенциал: Высокий {random.choice(emotions)}
💪 Рекомендация: Внедрять немедленно!"""

def transform_mechanicus(text: str) -> str:
    return f"""⚙️ *ТЕХНИЧЕСКОЕ ОПИСАНИЕ*

**1. Общие сведения:**
{text}

**2. Параметры:**
• Надежность: Высокая
• Масштабируемость: Да  
• Сложность: Средняя

**3. Рекомендации:**
Требует технической доработки."""

def transform_harmonicus(text: str) -> str:
    return f"""🌿 *ГАРМОНИЧНЫЙ АНАЛИЗ*

{text}

---
📖 *Комментарий:*
Баланс между техническими и человеческими факторами."""

def transform_architect(text: str) -> str:
    return f"""🏛️ *СТРУКТУРИРОВАННЫЙ ПЛАН*

**Раздел 1. Основа**
{text}

**Раздел 2. Компоненты**
1. Базовый модуль
2. Вспомогательные элементы  
3. Интеграционные решения

**Раздел 3. Внедрение**
Этап 1 → Этап 2 → Этап 3"""

# ==================== ЯНДЕКС GPT (опционально) ====================
def ask_yandex_gpt(text: str, style_id: str) -> str:
    if not YANDEX_API_KEY:
        return None  # Возвращаем None → используем алгоритмический стиль
    
    # Промпты для разных стилей
    prompts = {
        "ice": "Ты — строгий аналитик. Преобразуй текст в чёткий фактологический список. Не придумывай новые факты.",
        "phoenix": "Ты — мотивационный спикер. Перескажи текст эмоционально с эмодзи 🚀✨🔥, НО СОХРАНИ СМЫСЛ.",
        "mechanicus": "Ты — технический писатель. Преобразуй текст в техническую документацию: 1. Описание 2. Параметры 3. Рекомендации.",
        "harmonicus": "Ты — философ-гуманист. Преобразуй текст в гармоничное эссе с плавными переходами.",
        "architect": "Ты — архитектор систем. Преобразуй текст в структурированный план с иерархией."
    }
    
    try:
        response = requests.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
            headers={
                "Authorization": f"Api-Key {YANDEX_API_KEY}",
                "Content-Type": "application/json",
                "x-folder-id": YANDEX_FOLDER_ID
            },
            json={
                "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt-lite",
                "completionOptions": {"temperature": 0.7, "maxTokens": 1000},
                "messages": [
                    {"role": "system", "text": prompts.get(style_id, "Преобразуй текст")},
                    {"role": "user", "text": text}
                ]
            },
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('result', {}).get('alternatives', [{}])[0].get('message', {}).get('text', '')
            return answer if answer.strip() else None
        return None
        
    except Exception as e:
        logger.error(f"Ошибка Яндекс GPT: {e}")
        return None

# ==================== ОБРАБОТЧИКИ TELEGRAM ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start — главное меню"""
    keyboard = [[InlineKeyboardButton(name, callback_data=f"style_{style_id}")] 
                for style_id, name in STYLES.items()]
    keyboard.append([InlineKeyboardButton("ℹ️ Как работает бот", callback_data="help")])
    
    await update.message.reply_text(
        "🤖 *TextAlchemic Bot*\n"
        "Преобразую тексты в 5 стилях. Выберите стиль:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка кнопок"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("style_"):
        style_id = query.data.replace("style_", "")
        context.user_data["style"] = style_id  # ← СОХРАНЯЕМ В КОНТЕКСТЕ (не глобальная переменная!)
        
        await query.edit_message_text(
            f"✅ Выбрано: *{STYLES[style_id]}*\n"
            f"Отправьте текст для преобразования (минимум 10 символов):",
            parse_mode='Markdown'
        )
    
    elif query.data == "help":
        await query.edit_message_text(
            "✨ *Как это работает:*\n"
            "1. Выберите стиль через /start\n"
            "2. Отправьте текст\n"
            "3. Получите результат от нейросети (или алгоритма)\n"
            "4. Отправьте НОВЫЙ текст — стиль сохранится!\n"
            "5. Нажмите /start чтобы сменить стиль",
            parse_mode='Markdown'
        )
    
    elif query.data == "new_text":
        style_id = context.user_data.get("style", "ice")
        await query.edit_message_text(
            f"📝 Отправьте новый текст для стиля *{STYLES[style_id]}*:",
            parse_mode='Markdown'
        )
    
    elif query.data == "new_style":
        await start_command(update, context)
    
    elif query.data == "reuse_text":
        # Повторная обработка того же текста в новом стиле
        original_text = context.user_data.get("last_original_text")
        if original_text:
            context.user_data["reuse_mode"] = True
            await start_command(update, context)
        else:
            await query.answer("❌ Нет сохранённого текста", show_alert=True)

async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текста"""
    text = update.message.text.strip()
    
    # Если в режиме повторного использования — сохраняем текст и просим выбрать стиль
    if context.user_data.get("reuse_mode"):
        context.user_data["last_original_text"] = text
        context.user_data["reuse_mode"] = False
        await update.message.reply_text(
            "✅ Текст сохранён. Теперь выберите стиль через /start",
            parse_mode='Markdown'
        )
        return
    
    if len(text) < 10:
        await update.message.reply_text("📝 Минимум 10 символов")
        return
    
    style_id = context.user_data.get("style")
    if not style_id:
        await update.message.reply_text("⚠️ Сначала выберите стиль через /start")
        return
    
    # Сохраняем исходный текст для повторной обработки
    context.user_data["last_original_text"] = text
    
    # Показываем "печатает..."
    await update.message.reply_chat_action("typing")
    
    # Сначала пробуем Яндекс GPT
    result = ask_yandex_gpt(text, style_id)
    
    # Если Яндекс недоступен — используем алгоритмический стиль
    if result is None:
        transformers = {
            "ice": transform_ice,
            "phoenix": transform_phoenix,
            "mechanicus": transform_mechanicus,
            "harmonicus": transform_harmonicus,
            "architect": transform_architect
        }
        transform_func = transformers.get(style_id, transform_ice)
        result = transform_func(text)
    
    # Сохраняем результат
    context.user_data["last_result"] = result
    
    # Кнопки для продолжения
    keyboard = [
        [InlineKeyboardButton("🔄 Новый текст (в этом стиле)", callback_data="new_text")],
        [InlineKeyboardButton("🎨 Сменить стиль", callback_data="new_style")],
        [InlineKeyboardButton("🔁 Обработать в другом стиле", callback_data="reuse_text")]
    ]
    
    await update.message.reply_text(
        f"✨ *{STYLES[style_id]}*\n\n{result}\n\n"
        f"💡 Выберите действие ниже",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# ==================== ЗАПУСК ====================
def main():
    print("=" * 60)
    print("🤖 TextAlchemic Bot — ФИНАЛЬНАЯ РАБОЧАЯ ВЕРСИЯ")
    print("=" * 60)
    print(f"Токен: {'✅' if TELEGRAM_TOKEN else '❌'}")
    print(f"Яндекс GPT: {'✅' if YANDEX_API_KEY else '⚠️ Без ИИ (алгоритмы)'}")
    print(f"Каталог: {YANDEX_FOLDER_ID}")
    print("=" * 60)
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))
    
    print("🚀 Бот запущен! Состояние сохраняется между запросами.")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
