#!/usr/bin/env python3
"""
TextAlchemic Bot — МИНИМАЛЬНАЯ РАБОЧАЯ ВЕРСИЯ
Решает 2 проблемы: 
1. Состояние не сбрасывается между запросами
2. Ответы уникальны благодаря Яндекс GPT
"""
import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==================== ВРЕМЕННЫЕ КЛЮЧИ ДЛЯ ТЕСТА (УДАЛИТЬ ПОСЛЕ ПРОВЕРКИ!) ====================
TELEGRAM_TOKEN = "8542210651:AAG7Ze8DlRJwHrOYKPOrTqdnvJzLgcm23KQ"  # ← ВАШ ТОКЕН
YANDEX_API_KEY = "AQVN0crSDPUX8ih2oSeu6TbgAVekrefEYFP_JBU2"  # ← ЗАМЕНИТЕ НА РЕАЛЬНЫЙ КЛЮЧ!
YANDEX_FOLDER_ID = "b1gf28m0hpqbo55slm6d"  # ← ВАШ КАТАЛОГ

# ==================== ПРОМПТЫ ДЛЯ СТИЛЕЙ (копия из prompts.json) ====================
PROMPTS = {
    "ice": "Ты — строгий аналитик. Преобразуй текст в чёткий фактологический список. Не придумывай новые факты. Формат: 1. Факт 1\n2. Факт 2\n3. Факт 3",
    "phoenix": "Ты — мотивационный спикер. Перескажи текст эмоционально с эмодзи 🚀✨🔥💪🎯 и хештегами (#Успех #Развитие), НО СОХРАНИ СМЫСЛ. Не искажай факты.",
    "mechanicus": "Ты — технический писатель. Преобразуй текст в техническую документацию: 1. Описание 2. Параметры 3. Рекомендации. Используй только информацию из текста.",
    "harmonicus": "Ты — философ-гуманист. Преобразуй текст в гармоничное эссе с плавными переходами. Сохрани все ключевые идеи, не добавляй новые концепции.",
    "architect": "Ты — архитектор систем. Преобразуй текст в структурированный план с иерархией: 1. Основная концепция → 1.1. Элементы → 1.2. Взаимосвязи"
}

STYLES_INFO = {
    "ice": {"name": "Лёд ❄️", "desc": "Факты списком"},
    "phoenix": {"name": "Феникс 🔥", "desc": "Эмоционально с эмодзи"},
    "mechanicus": {"name": "Механик ⚙️", "desc": "Техдокументация"},
    "harmonicus": {"name": "Гармония 🌿", "desc": "Гармоничное эссе"},
    "architect": {"name": "Архитектор 🏛️", "desc": "Структурированный план"}
}

# ==================== ЗАПРОС К ЯНДЕКС GPT ====================
def ask_yandex_gpt(text: str, style_id: str) -> str:
    """Безопасный запрос к Яндекс GPT"""
    if not YANDEX_API_KEY:
        return "❌ Яндекс GPT не настроен. Добавьте ключ в код."
    
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
            timeout=20
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('result', {}).get('alternatives', [{}])[0].get('message', {}).get('text', '')
            return answer if answer.strip() else "🤔 Яндекс GPT вернул пустой ответ"
        else:
            return f"❌ Ошибка Яндекс GPT: {response.status_code}"
            
    except requests.exceptions.Timeout:
        return "⏱️ Таймаут запроса (20 сек). Попробуйте короткий текст."
    except Exception as e:
        return f"💥 Ошибка: {str(e)[:150]}"

# ==================== ОБРАБОТЧИКИ TELEGRAM ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    keyboard = [[InlineKeyboardButton(info['name'], callback_data=f"style_{style_id}")] 
                for style_id, info in STYLES_INFO.items()]
    keyboard.append([InlineKeyboardButton("ℹ️ Как это работает", callback_data="help")])
    
    await update.message.reply_text(
        "🤖 *TextAlchemic Bot*\n"
        "Преобразую любой текст в 5 стилях через нейросеть Яндекса.\n"
        "Выберите стиль:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка кнопок"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("style_"):
        style_id = query.data.replace("style_", "")
        context.user_data["style"] = style_id  # ← КЛЮЧ: безопасное хранение в контексте!
        
        await query.edit_message_text(
            f"✅ Выбрано: *{STYLES_INFO[style_id]['name']}*\n"
            f"_{STYLES_INFO[style_id]['desc']}_\n\n"
            "Отправьте текст для преобразования (минимум 10 символов):",
            parse_mode='Markdown'
        )
    
    elif query.data == "help":
        await query.edit_message_text(
            "✨ *Как это работает:*\n"
            "1. Выберите стиль через /start\n"
            "2. Отправьте любой текст\n"
            "3. Получите уникальный результат от нейросети Яндекса\n"
            "4. Отправьте новый текст — стиль сохранится!\n"
            "5. Нажмите /start чтобы сменить стиль",
            parse_mode='Markdown'
        )

async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текста"""
    text = update.message.text.strip()
    
    if len(text) < 10:
        await update.message.reply_text("📝 Минимум 10 символов")
        return
    
    style_id = context.user_data.get("style", "ice")  # ← Безопасное получение из контекста
    if style_id not in STYLES_INFO:
        await update.message.reply_text("⚠️ Сначала выберите стиль через /start")
        return
    
    # Обработка
    await update.message.reply_chat_action("typing")  # Показывает "печатает..."
    result = ask_yandex_gpt(text, style_id)
    
    # Отправка результата
    await update.message.reply_text(
        f"✨ *{STYLES_INFO[style_id]['name']}*\n\n{result}\n\n"
        f"💡 Отправьте новый текст для продолжения в этом стиле",
        parse_mode='Markdown'
    )

# ==================== ЗАПУСК ====================
def main():
    print("=" * 60)
    print("🤖 TextAlchemic Bot — МИНИМАЛЬНАЯ РАБОЧАЯ ВЕРСИЯ")
    print("=" * 60)
    print(f"Токен: {'✅' if TELEGRAM_TOKEN else '❌'}")
    print(f"Яндекс GPT: {'✅' if YANDEX_API_KEY != 'ВАШ_КЛЮЧ_ЯНДЕКСА_СЮДА' else '❌'}")
    print(f"Каталог: {YANDEX_FOLDER_ID}")
    print("=" * 60)
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))
    
    print("🚀 Бот запущен! Для остановки нажмите Ctrl+C")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
