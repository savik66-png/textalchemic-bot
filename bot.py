import asyncio
import io
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from config import BOT_TOKEN
from session_manager import session_manager
from core import text_processor # Импорт модуля text_processor из пакета core

# --- Создание бота и диспетчера ---
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Глобальные переменные для пагинации ---
STYLES_PER_PAGE = 8 # Количество стилей на одной странице

# --- Вспомогательные функции ---

def get_styles_keyboard(page_num: int = 0):
    """Создаёт клавиатуру с выбором стиля, разбитую на страницы."""
    styles_list = text_processor.get_available_styles_list()
    
    if not styles_list or styles_list[0].startswith("Ошибка"):
         # Если не удалось загрузить стили, создаём простую клавиатуру
         styles_list = ["spell. Правка 📝", "ice. Лёд ❄️", "phoenix. Феникс 🔥"] # Резервный вариант
    
    total_pages = (len(styles_list) + STYLES_PER_PAGE - 1) // STYLES_PER_PAGE # Округление вверх
    page_num = max(0, min(page_num, total_pages - 1)) # Ограничение номера страницы
    
    start_idx = page_num * STYLES_PER_PAGE
    end_idx = start_idx + STYLES_PER_PAGE
    current_page_styles = styles_list[start_idx:end_idx]
    
    # Создаём кнопки для текущей страницы (2 в ряд)
    buttons = []
    for i in range(0, len(current_page_styles), 2):
        row = [KeyboardButton(text=current_page_styles[i])]
        if i + 1 < len(current_page_styles):
            row.append(KeyboardButton(text=current_page_styles[i+1]))
        buttons.append(row)

    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True # Клавиатура исчезнет после выбора
    )
    
    return keyboard, page_num, total_pages

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
        "Я могу трансформировать ваш текст под разные цели:\n"
        "🎯 **Блогеры & SMM:** посты для соцсетей и мессенджеров\n"
        "📰 **Журналисты:** статьи и пресс-релизы\n"
        "🔬 **Учёные & Методисты:** доклады и методики\n"
        "💼 **Бизнес & Стартапы:** письма, тизеры, презентации\n"
        "📝 **Общее:** проверка орфографии, суть текста, факты списком и др.\n\n"
        "📄 Также могу обрабатывать *текстовые файлы* (.txt).\n\n"
        "<b>ВАЖНО:</b> Если вы не видите нужный стиль внизу, "
        "проведите пальцем по клавиатуре вниз — их много!\n\n"
        "Теперь пришли мне текст или файл .txt для обработки."
    )
    # Получаем клавиатуру для первой страницы стилей
    styles_keyboard, current_page, total_pages = get_styles_keyboard(0)
    
    await message.answer(welcome_text, reply_markup=styles_keyboard, parse_mode='HTML')
    # Показываем счётчик страниц ТОЛЬКО если их больше одной
    if total_pages > 1:
        await message.answer(f"(Стр. {current_page + 1}/{total_pages}). Выберите стиль или используйте навигацию (если доступна).")
    #else:
    #    await message.answer("Выберите стиль из списка ниже:")


@dp.callback_query(F.data.startswith("styles_page_")) # Хэндлер для навигации по страницам (опционально, если переделаем на inline)
async def navigate_styles(call):
    await call.answer() # Отвечаем на callback
    try:
        page_num = int(call.data.split('_')[2])
        styles_keyboard, current_page, total_pages = get_styles_keyboard(page_num)
        await call.message.edit_reply_markup(reply_markup=styles_keyboard) # Попытка обновить клавиатуру (не работает с ReplyKeyboard)
        # Так как ReplyKeyboard не обновляется, просто пошлём новое сообщение с инструкцией
        if total_pages > 1:
            await call.message.answer(f"(Стр. {current_page + 1}/{total_pages}). Выберите стиль.")
        #else:
        #    await call.message.answer("Выберите стиль из списка ниже.")
    except (IndexError, ValueError):
        await call.message.answer("❌ Ошибка навигации по стилям.")


@dp.message(F.text & F.text.lower().contains('начать сначала'))
async def cmd_restart(message: Message):
    user_id = message.from_user.id
    session_manager.create_session(user_id) # Сбрасываем сессию
    await message.answer("Сессия сброшена. Пришли новый текст или файл.", reply_markup=get_start_keyboard())


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
        # Отправляем обновлённую клавиатуру стилей для файла
        styles_keyboard, current_page, total_pages = get_styles_keyboard(0)
        style_choice_text = f"Файл загружен ({len(original_text)} символов). Теперь выбери, в каком стиле обработать текст:"
        await message.answer(style_choice_text, reply_markup=styles_keyboard)
        # Показываем счётчик страниц ТОЛЬКО если их больше одной
        if total_pages > 1:
            await message.answer(f"(Стр. {current_page + 1}/{total_pages}). Выберите стиль.")


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
        # Отправляем обновлённую клавиатуру стилей для текста
        styles_keyboard, current_page, total_pages = get_styles_keyboard(0)
        style_choice_text = "Теперь выбери, в каком стиле обработать текст:"
        await message.answer(style_choice_text, reply_markup=styles_keyboard)
        # Показываем счётчик страниц ТОЛЬКО если их больше одной
        if total_pages > 1:
            await message.answer(f"(Стр. {current_page + 1}/{total_pages}). Выберите стиль.")

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
