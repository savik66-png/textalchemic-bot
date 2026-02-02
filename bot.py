import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from config import BOT_TOKEN
from session_manager import session_manager
from core import text_processor # Импорт модуля text_processor из пакета core

# --- Создание бота и диспетчера ---
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Вспомогательные функции ---

def get_styles_keyboard():
    """Создаёт клавиатуру с выбором стиля."""
    styles_list = text_processor.get_available_styles_list()
    if not styles_list or styles_list[0].startswith("Ошибка"):
         # Если не удалось загрузить стили, создаём простую клавиатуру
         styles_list = ["spell. Правка 📝", "ice. Лёд ❄️", "phoenix. Феникс 🔥"] # Резервный вариант

    buttons = [[KeyboardButton(text=s)] for s in styles_list]
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True # Клавиатура исчезнет после выбора
    )
    return keyboard

def get_start_keyboard():
    """Клавиатура при /start."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔄 Начать сначала")]],
        resize_keyboard=True
    )
    return keyboard

# --- Хэндлеры ---

@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    session_manager.create_session(user_id) # Сбрасываем сессию

    welcome_text = (
        "✨ Привет! Я TextAlchemic — твой помощник для идеального текста.\n\n"
        "Отправь мне любой текст, который нужно улучшить. Я могу сделать его:\n"
    )
    # Получаем список стилей и добавляем к приветствию
    styles_list = text_processor.get_available_styles_list()
    if not styles_list or styles_list[0].startswith("Ошибка"):
        welcome_text += "\n⚠️ [DEBUG] Ошибка загрузки списка стилей."
    else:
        for s in styles_list:
            welcome_text += f"\n{s}"

    welcome_text += "\n\nСначала пришли текст, который хочешь обработать."
    await message.answer(welcome_text, reply_markup=get_start_keyboard())

@dp.message(F.text & F.text.lower().contains('начать сначала'))
async def cmd_restart(message: Message):
    user_id = message.from_user.id
    session_manager.create_session(user_id) # Сбрасываем сессию
    await message.answer("Сессия сброшена. Пришли новый текст.")

@dp.message(F.text & ~F.text.startswith('/'))
async def handle_text_and_states(message: Message):
    user_id = message.from_user.id
    text = message.text.strip()

    session = session_manager.get_or_create_session(user_id)
    state = session["state"]

    if state == "waiting_for_text":
        if len(text) < 5: # Простая проверка на минимальный размер текста
             await message.answer("Пожалуйста, пришли немного более подробный текст для обработки.")
             return

        session_manager.update_session_state(user_id, "waiting_for_style", original_text=text)
        style_choice_text = "Теперь выбери, в каком стиле обработать текст:"
        await message.answer(style_choice_text, reply_markup=get_styles_keyboard())

    elif state == "waiting_for_style":
        # Проверяем, является ли сообщение выбором стиля (например, "spell. ...", "ice. ...")
        # Извлекаем ID стиля из начала сообщения
        selected_style_id = None
        available_styles = text_processor.get_available_styles_list()
        for style_desc in available_styles:
            if text.startswith(f"{style_desc.split('.')[0]}."): # Берём ID до точки
                selected_style_id = style_desc.split('.')[0]
                break

        if selected_style_id:
            original_text = session["original_text"]

            # --- Вызов обработчика стиля ---
            await message.answer("Обрабатываю текст... ⏳")
            processed_text = text_processor.process_text_with_style(original_text, selected_style_id)

            final_response = f"✨ Ваш улучшенный текст ({selected_style_id}):\n\n{processed_text}"

            # Сбрасываем сессию после ответа
            session_manager.create_session(user_id)

            await message.answer(final_response, reply_markup=get_start_keyboard())
        else:
            # Если пользователь снова прислал текст, а не выбрал стиль
            await message.answer("Пожалуйста, выбери стиль из предложенных кнопок.")


# --- Запуск ---
async def main():
    print("Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
