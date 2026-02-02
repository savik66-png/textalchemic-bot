#!/usr/bin/env python3
"""
TextAlchemic Bot — МИНИМАЛЬНАЯ РАБОЧАЯ ВЕРСИЯ
НЕТ глобальных переменных. ТОЛЬКО context.user_data.
"""
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8542210651:AAG7Ze8DlRJwHrOYKPOrTqdnvJzLgcm23KQ')

STYLES = {
    "ice": "Лёд ❄️",
    "phoenix": "Феникс 🔥",
    "mechanicus": "Механик ⚙️",
    "harmonicus": "Гармония 🌿",
    "architect": "Архитектор 🏛️"
}

def transform_ice(text):
    return f"❄️ *КЛЮЧЕВЫЕ ФАКТЫ:*\n1. {text[:30]}...\n2. Анализ завершён"

def transform_phoenix(text):
    return f"🔥 *ЭМОЦИОНАЛЬНЫЙ АНАЛИЗ*\n✨ {text}\n\n#Успех #Развитие"

def transform_mechanicus(text):
    return f"⚙️ *ТЕХДОКУМЕНТАЦИЯ:*\nОписание: {text[:50]}..."

def transform_harmonicus(text):
    return f"🌿 *ГАРМОНИЯ:*\n{text}\n\n📖 Баланс достигнут"

def transform_architect(text):
    return f"🏛️ *ПЛАН:*\n1. {text[:30]}...\n2. Этап реализации"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton(name, callback_data=f"s_{sid}")] for sid, name in STYLES.items()]
    await update.message.reply_text("🤖 Выберите стиль:", reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data.startswith("s_"):
        sid = q.data[2:]
        context.user_data["style"] = sid
        await q.edit_message_text(f"✅ *{STYLES[sid]}*\nОтправьте текст (10+ символов):", parse_mode='Markdown')

async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text.strip()
    if len(txt) < 10:
        await update.message.reply_text("📝 Минимум 10 символов")
        return
    sid = context.user_data.get("style")
    if not sid:
        await update.message.reply_text("⚠️ Сначала /start → выберите стиль")
        return
    funcs = {"ice": transform_ice, "phoenix": transform_phoenix, "mechanicus": transform_mechanicus, "harmonicus": transform_harmonicus, "architect": transform_architect}
    res = funcs.get(sid, transform_ice)(txt)
    kb = [[InlineKeyboardButton("🔄 Новый текст", callback_data="nt")], [InlineKeyboardButton("🎨 Сменить стиль", callback_data="cs")]]
    await update.message.reply_text(f"✨ *{STYLES[sid]}*\n\n{res}", reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')

async def cont(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "nt":
        sid = context.user_data.get("style", "ice")
        await q.edit_message_text(f"📝 Новый текст для *{STYLES[sid]}*:", parse_mode='Markdown')
    elif q.data == "cs":
        await start(update, context)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button, pattern="^s_"))
    app.add_handler(CallbackQueryHandler(cont, pattern="^(nt|cs)$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
