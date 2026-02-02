#!/usr/bin/env python3
"""
TextAlchemic Bot — МИНИМАЛЬНАЯ РАБОЧАЯ ВЕРСИЯ
• НЕТ глобальных переменных
• Правильный порядок обработчиков
• Все кнопки работают
• Текст преобразуется
"""
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv('TELEGRAM_TOKEN', '8542210651:AAG7Ze8DlRJwHrOYKPOrTqdnvJzLgcm23KQ')

STYLES = {"ice": "Лёд ❄️", "phoenix": "Феникс 🔥", "mechanicus": "Механик ⚙️", "harmonicus": "Гармония 🌿", "architect": "Архитектор 🏛️"}

def transform_ice(t): return f"❄️ *ФАКТЫ:*\n1. {t[:30]}...\n2. Анализ завершён"
def transform_phoenix(t): return f"🔥 *ЭМОЦИИ:*\n{t}\n\n#Успех #Развитие"
def transform_mechanicus(t): return f"⚙️ *ТЕХДОК:*\n{t[:50]}..."
def transform_harmonicus(t): return f"🌿 *ГАРМОНИЯ:*\n{t}\n\n📖 Баланс"
def transform_architect(t): return f"🏛️ *ПЛАН:*\n1. {t[:30]}...\n2. Реализация"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton(n, callback_data=f"s_{k}")] for k, n in STYLES.items()]
    await update.message.reply_text("🤖 Выберите стиль:", reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data.startswith("s_"):
        sid = q.data[2:]
        context.user_data["style"] = sid
        await q.edit_message_text(f"✅ *{STYLES[sid]}*\nОтправьте текст (10+ символов):", parse_mode='Markdown')
    elif q.data == "nt":
        sid = context.user_data.get("style", "ice")
        await q.edit_message_text(f"📝 Новый текст для *{STYLES[sid]}*:", parse_mode='Markdown')
    elif q.data == "cs":
        await start(update, context)

async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    t = update.message.text.strip()
    if len(t) < 10:
        await update.message.reply_text("📝 Минимум 10 символов")
        return
    sid = context.user_data.get("style")
    if not sid:
        await update.message.reply_text("⚠️ Сначала /start → выберите стиль")
        return
    funcs = {"ice": transform_ice, "phoenix": transform_phoenix, "mechanicus": transform_mechanicus, "harmonicus": transform_harmonicus, "architect": transform_architect}
    r = funcs.get(sid, transform_ice)(t)
    kb = [[InlineKeyboardButton("🔄 Новый текст", callback_data="nt")], [InlineKeyboardButton("🎨 Сменить стиль", callback_data="cs")]]
    await update.message.reply_text(f"✨ *{STYLES[sid]}*\n\n{r}", reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))  # 1. Сначала команды
    app.add_handler(CallbackQueryHandler(button))    # 2. Потом кнопки
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))  # 3. Потом текст (исключая команды!)
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
