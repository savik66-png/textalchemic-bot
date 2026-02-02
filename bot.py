import asyncio
import io
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
        "Отправь мне любой текст или текстовый файл (.txt), который нужно улучшить. Я могу сделать его:\n"
    )
    # Получаем список стилей и добавляем к приветствию
    styles_list = text_processor.get_available_styles_list()
    if not styles_list or styles_list[0].startswith("Ошибка"):
        welcome_text += "\n⚠️ [DEBUG] Ошибка загрузки списка стилей."
    else:
        for s in styles_list:
            welcome_text += f"\n{s}"

    welcome_text += "\n\nСначала пришли текст или файл .txt."
    await message.answer(welcome_text, reply_markup=get_start_keyboard())

@dp.message(F.text & F.text.lower().contains('начать сначала'))
async def cmd_restart(message: Message):
    user_id = message.from_user.id
    session_manager.create_session(user_id) # Сбрасываем сессию
    await message.answer("Сессия сброшена. Пришли новый текст или файл.")

# --- НОВЫЙ ХЭНДЛЕР: Обработка документов (.txt) ---
@dp.message(F.document & F.document.mime_type == 'text/plain')
async def handle_txt_document(message: Message):
    user_id = message.from_user.id
    document = message.document
    file_info = await bot.get_file(document.file_id)
    file_path = file_info.file_path

    # Скачиваем файл в память (BytesIO)
    file_content_bytes = await bot.download_file(file_path)
    try:
        # Декодируем содержимое файла в строку (предполагаем UTF-8)
        original_text = file_content_bytes.read().decode('utf-8').strip()
    except UnicodeDecodeError:
        await message.answer("❌ Ошибка: невозможно декодировать файл. Убедитесь, что файл в формате .txt и кодировке UTF-8.")
        return # Прерываем обработку
    except Exception as e:
        print(f"[ERROR] Ошибка при чтении файла: {e}")
        await message.answer("❌ Ошибка при чтении файла.")
        return # Прерываем обработку

    if not original_text:
        await message.answer("❌ Файл пустой.")
        return # Прерываем обработку

    # Логика аналогична handle_text_and_states для состояния waiting_for_text
    session = session_manager.get_or_create_session(user_id)
    # session_manager.update_session_state(user_id, "waiting_for_style", original_text=original_text) # Если хотим, чтобы выбор стиля происходил после загрузки файла
    # Но логичнее, чтобы стиль был выбран *до* загрузки файла, чтобы пользователь знал, что получит.
    # Поэтому, если пользователь не в состоянии ожидания стиля, считаем, что он хочет применить стиль к файлу.
    # Проверим состояние:
    state = session["state"]
    if state == "waiting_for_style":
        # Стиль уже выбран, обрабатываем текст из файла
        selected_style_id = session["selected_style_id"]
        if not selected_style_id:
             await message.answer("❌ Произошла ошибка: стиль не выбран. Начните сначала.")
             session_manager.create_session(user_id)
             return

        await message.answer("Обрабатываю текст из файла... ⏳")
        processed_text = text_processor.process_text_with_style(original_text, selected_style_id)

        # --- Отправка результата ---
        # Ограничиваем длину сообщения для Telegram
        MAX_TELEGRAM_MESSAGE_LENGTH = 4096
        if len(processed_text) > MAX_TELEGRAM_MESSAGE_LENGTH:
            await message.answer("Обработанный текст слишком длинный. Отправляю частями...")

            parts = [processed_text[i:i+MAX_TELEGRAM_MESSAGE_LENGTH] for i in range(0, len(processed_text), MAX_TELEGRAM_MESSAGE_LENGTH)]
            for part in parts:
                await message.answer(part)
        else:
            await message.answer(processed_text)

        # Сбрасываем сессию после обработки
        session_manager.create_session(user_id)
        await message.answer("✅ Обработка файла завершена.", reply_markup=get_start_keyboard())
    else:
        # Если пользователь не ожидал стиля, значит, он прислал файл без предварительного выбора стиля.
        # Запоминаем текст из файла и переходим к выбору стиля.
        session_manager.update_session_state(user_id, "waiting_for_style", original_text=original_text)
        style_choice_text = f"Файл загружен ({len(original_text)} символов). Теперь выбери, в каком стиле обработать текст:"
        await message.answer(style_choice_text, reply_markup=get_styles_keyboard())


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

            # --- Отправка результата ---
            MAX_TELEGRAM_MESSAGE_LENGTH = 4096
            if len(processed_text) > MAX_TELEGRAM_MESSAGE_LENGTH:
                await message.answer("Обработанный текст слишком длинный. Отправляю частями...")

                parts = [processed_text[i:i+MAX_TELEGRAM_MESSAGE_LENGTH] for i in range(0, len(processed_text), MAX_TELEGRAM_MESSAGE_LENGTH)]
                for part in parts:
                    await message.answer(part)
            else:
                await message.answer(processed_text)

            # Сбрасываем сессию после ответа
            session_manager.create_session(user_id)

            await message.answer("✅ Обработка текста завершена.", reply_markup=get_start_keyboard())
        else:
            # Если пользователь снова прислал текст, а не выбрал стиль
            await message.answer("Пожалуйста, выбери стиль из предложенных кнопок.")


# --- Запуск ---
async def main():
    print("Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
