import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токен из переменных окружения
TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    await update.message.reply_html(
        f"Привет, {user.mention_html()}! 👋\n"
        f"Я бот проекта TextAlchemic.\n"
        f"Просто напиши мне что-нибудь, и я отвечу."
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ответ на любое текстовое сообщение"""
    user_text = update.message.text
    await update.message.reply_text(
        f"✅ Получил ваше сообщение:\n"
        f"«{user_text}»\n\n"
        f"Текст обработан системой TextAlchemic."
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Ошибка: {context.error}")

def main():
    """Основная функция запуска бота"""
    if not TOKEN:
        logger.error("❌ Токен не найден! Проверьте переменную окружения BOT_TOKEN")
        return
    
    print("✅ Бот запускается...")
    print(f"🔑 Токен: {TOKEN[:10]}...")
    
    # Создаем приложение
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    print("🤖 Бот запущен и готов к работе!")
    print("ℹ️  Напишите боту в Telegram: /start")
    application.run_polling()

if __name__ == '__main__':
    main()
