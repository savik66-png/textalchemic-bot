import os
print("✅ Бот запускается...")
TOKEN = os.environ.get("BOT_TOKEN")
print(f"Токен: {TOKEN[:10] if TOKEN else 'НЕТУ'}")
print("Если токен есть выше - бот заработает")
