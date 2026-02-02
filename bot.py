#!/usr/bin/env python3
"""
TextAlchemic Bot — ИСПРАВЛЕННАЯ ВЕРСИЯ
Решает проблему сброса состояния на облачном хостинге
"""
import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==================== НАСТРОЙКИ ====================
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8542210651:AAG7Ze8DlRJwHrOYKPOrTqdnvJzLgcm23KQ')
YANDEX_API_KEY = os.getenv('YANDEX_API_KEY', '')  # Оставьте пустым если нет ключа
YANDEX_FOLDER_ID = os.getenv('YANDEX_FOLDER_ID', 'b1gf28m0hpqbo55slm6d')  # ← ВАШ ПРАВИЛЬНЫЙ КАТАЛОГ!

# ==================== ЛОГИРОВАНИЕ ====================
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== ПРОМПТЫ ДЛЯ СТИЛЕЙ ====================
PROMPTS = {
    "ice": "Ты — строгий аналитик. Преобразуй текст в чёткий фактологический список. Не придумывай новые факты. Формат: 1. Факт 1\n2. Факт 2",
    "phoenix": "Ты — мотивационный спикер. Перескажи текст эмоционально с эмодзи 🚀✨🔥 и хештегами (#Успех #Развитие), НО СОХРАНИ СМЫСЛ.",
    "mechanicus": "Ты — технический писатель. Преобразуй текст в техническую документацию: 1. Описание 2. Параметры 3. Рекомендации.",
    "harmonicus": "Ты — философ-гуманист. Преобразуй текст в гармоничное эссе с плавными переходами. Сохрани все ключевые идеи.",
    "architect": "Ты — архитектор систем. Преобразуй текст в структурированный план с иерархией: 1. Основная концепция → 1.1. Элементы"
}

STYLES = {
    "ice": "Лёд ❄️",
    "phoenix": "Феникс 🔥",
    "mechanicus": "Механик ⚙️",
    "harmonicus": "Гармония 🌿",
    "architect": "Архитектор 🏛️"
}

# ==================== ЗАПРОС К ЯНДЕКС GPT ====================
def ask_yandex_gpt(text: str, style_id: str) -> str:
    if not YANDEX_API_KEY:
        # Резервный алгоритмический вариант (без ИИ)
        fallbacks = {
            "ice": f"❄️ *ФАКТЫ:*\n1. {text[:30]}...\n2. Анализ завершён",
            "phoenix": f"🔥 *ЭМОЦИИ:*\n{text}\n\n✨ #Успех #Развитие",
            "mechanicus": f"⚙️ *ТЕХДОКУМЕНТАЦИЯ:*\nОписание: {text[:50]}...",
            "harmonicus": f"🌿 *ГАРМОНИЯ:*\n{text}\n\n📖 Баланс достигнут",
            "architect": f"🏛️ *ПЛАН:*\n1. {text[:30]}...\n2. Этап реализации"
        }
        return fallbacks.get(style_id, text)
    
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
                    {"role": "system", "text": PROMPTS[style_id]},
                    {"role": "user", "text": text}
                ]
            },
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('result', {}).get('alternatives', [{}])[0].get('message', {}).get('text', '')
            return answer if answer.strip() else "🤔 Нейросеть вернула пустой ответ"
        else:
            return f"❌ Ошибка Яндекс GPT: {response.status_code}"
            
    except requests.exceptions.Timeout:
        return "⏱️ Таймаут (15 сек). Попробуйте короткий текст."
    except Exception as e:
        return f"💥 Ошибка: {str(e)[:150]}"

# ==================== ОБРАБОТЧИКИ TELEGRAM ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("style_"):
        style_id = query.data.replace("style_", "")
        context.user_data["style"] = style_id  # ← КЛЮЧ: данные сохраняются между запросами!
        
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

async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    if len(text) < 10:
        await update.message.reply_text("📝 Минимум 10 символов")
        return
    
    style_id = context.user_data.get("style")  # ← Безопасное получение из контекста
    
    if not style_id:
        await update.message.reply_text("⚠️ Сначала выберите стиль через /start")
        return
    
    # Показываем "печатает..."
    await update.message.reply_chat_action("typing")
    
    # Обрабатываем текст
    result = ask_yandex_gpt(text, style_id)
    
    # Отправляем результат с кнопками для продолжения
    keyboard = [
        [InlineKeyboardButton("🔄 Новый текст (в этом стиле)", callback_data="new_text")],
        [InlineKeyboardButton("🎨 Сменить стиль", callback_data="new_style")]
    ]
    
    await update.message.reply_text(
        f"✨ *{STYLES[style_id]}*\n\n{result}\n\n"
        f"💡 Отправьте новый текст или используйте кнопки ниже",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def continue_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "new_text":
        style_id = context.user_data.get("style", "ice")
        await query.edit_message_text(
            f"📝 Отправьте новый текст для стиля *{STYLES[style_id]}*:",
            parse_mode='Markdown'
        )
    elif query.data == "new_style":
        await start_command(update, context)

# ==================== ЗАПУСК ====================
def main():
    print("=" * 60)
    print("🤖 TextAlchemic Bot — ИСПРАВЛЕННАЯ ВЕРСИЯ")
    print("=" * 60)
    print(f"Токен: {'✅' if TELEGRAM_TOKEN else '❌'}")
    print(f"Яндекс GPT: {'✅' if YANDEX_API_KEY else '⚠️ Без ИИ (алгоритмы)'}")
    print(f"Каталог: {YANDEX_FOLDER_ID}")
    print("=" * 60)
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^style_"))
    app.add_handler(CallbackQueryHandler(continue_handler, pattern="^(new_text|new_style)$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))
    
    print("🚀 Бот запущен! Состояние сохраняется между запросами.")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
