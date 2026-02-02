#!/usr/bin/env python3
"""
TextAlchemic Bot - МИНИМАЛЬНАЯ РАБОЧАЯ ВЕРСИЯ
Без глобального состояния → работает на любом хостинге
"""
import os
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==================== НАСТРОЙКИ (временно вшиты для теста) ====================
TELEGRAM_TOKEN = "8542210651:AAG7Ze8DlRJwHrOYKPOrTqdnvJzLgcm23KQ"  # ← ВРЕМЕННО ДЛЯ ТЕСТА!
YANDEX_API_KEY = ""  # Оставьте пустым пока не заработает база
YANDEX_FOLDER_ID = "b1gf28m0hpqbo55slm6d"  # ← ВАШ ПРАВИЛЬНЫЙ КАТАЛОГ!

# ==================== НАСТРОЙКА ЛОГИРОВАНИЯ ====================
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== АЛГОРИТМИЧЕСКИЕ СТИЛИ (без ИИ) ====================
def transform_ice(text: str) -> str:
    facts = ["Улучшение производительности", "Оптимизация процессов", "Снижение затрат", "Рост качества", "Автоматизация рутины"]
    selected = random.sample(facts, min(5, len(facts)))
    lines = ["❄️ *КЛЮЧЕВЫЕ ФАКТЫ:*"] + [f"{i}. {fact}." for i, fact in enumerate(selected, 1)]
    lines.append(f"\n📌 *Вывод:* Текст содержит {len(text.split())} слов.")
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

**2. Технические параметры:**
• Надежность: Высокая
• Масштабируемость: Да  
• Сложность внедрения: Средняя

**3. Рекомендации:**
Проект требует технической доработки."""

def transform_harmonicus(text: str) -> str:
    return f"""🌿 *ГАРМОНИЧНЫЙ АНАЛИЗ*

{text}

---
📖 *Комментарий:*
Представленный текст демонстрирует баланс между различными аспектами.
Рекомендуется учитывать как технические, так и человеческие факторы."""

def transform_architect(text: str) -> str:
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
Этап 3: Контроль"""

# ==================== ОБРАБОТЧИКИ ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("❄️ Лёд", callback_data="style_ice")],
        [InlineKeyboardButton("🔥 Феникс", callback_data="style_phoenix")],
        [InlineKeyboardButton("⚙️ Механик", callback_data="style_mechanicus")],
        [InlineKeyboardButton("🌿 Гармония", callback_data="style_harmonicus")],
        [InlineKeyboardButton("🏛️ Архитектор", callback_data="style_architect")]
    ]
    await update.message.reply_text(
        "🤖 *TextAlchemic Bot*\n"
        "Выберите стиль преобразования:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("style_"):
        style = query.data.replace("style_", "")
        context.user_data["selected_style"] = style  # ← Хранение в безопасном месте!
        
        examples = {
            "ice": "Наш проект улучшает работу отделов",
            "phoenix": "Мы создали революционный продукт!",
            "mechanicus": "Система состоит из модулей А, Б и В",
            "harmonicus": "Баланс технологий и человеческого подхода",
            "architect": "План реализации проекта в три этапа"
        }
        
        style_names = {
            "ice": "Лёд ❄️",
            "phoenix": "Феникс 🔥",
            "mechanicus": "Механик ⚙️",
            "harmonicus": "Гармония 🌿",
            "architect": "Архитектор 🏛️"
        }
        
        await query.edit_message_text(
            f"✅ Выбрано: *{style_names[style]}*\n"
            f"Отправьте текст для преобразования (минимум 5 символов):\n"
            f"💡 Пример: `{examples.get(style, 'Ваш текст')}`",
            parse_mode='Markdown'
        )

async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    if len(text) < 5:
        await update.message.reply_text("📝 Минимум 5 символов")
        return
    
    style = context.user_data.get("selected_style", "ice")  # ← Безопасное получение!
    
    # Выбор функции преобразования
    transformers = {
        "ice": transform_ice,
        "phoenix": transform_phoenix,
        "mechanicus": transform_mechanicus,
        "harmonicus": transform_harmonicus,
        "architect": transform_architect
    }
    
    transform_func = transformers.get(style, transform_ice)
    result = transform_func(text)
    
    # Отправка результата
    await update.message.reply_text(
        f"✨ *Результат:*\n\n{result}\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📊 Символов: {len(result)}\n"
        f"🔄 Чтобы преобразовать новый текст — просто отправьте его!",
        parse_mode='Markdown'
    )

# ==================== ЗАПУСК ====================
def main():
    print("=" * 60)
    print("🤖 TextAlchemic Bot — МИНИМАЛЬНАЯ РАБОЧАЯ ВЕРСИЯ")
    print("=" * 60)
    print("✅ Без глобального состояния")
    print("✅ Работает на любом хостинге")
    print("✅ 5 алгоритмических стилей")
    print("=" * 60)
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))
    
    print("🚀 Бот запущен! Для остановки нажмите Ctrl+C")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
