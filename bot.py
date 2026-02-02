import asyncio
import io
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from config import BOT_TOKEN
from session_manager import session_manager
from core import text_processor # Импорт модуля text_processor из пакета core

# --- Создание бота и диспетчера ---
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Глобальные переменные для пагинации ---
STYLES_PER_PAGE = 8 # Количество стилей на одной странице

# --- Вспомогательные функции ---

def get_styles_inline_keyboard(page_num: int = 0):
    """Создаёт inline-клавиатуру с выбором стиля и навигацией."""
    styles_list = text_processor.get_available_styles_list()
    
    if not styles_list or styles_list[0].startswith("Ошибка"):
         # Если не удалось загрузить стили, создаём простую клавиатуру
         styles_list = ["spell. Правка 📝", "ice. Лёд ❄️", "phoenix. Феникс 🔥"] # Резервный вариант
    
    total_pages = (len(styles_list) + STYLES_PER_PAGE - 1) // STYLES_PER_PAGE # Округление вверх
    page_num = max(0, min(page_num, total_pages - 1)) # Ограничение номера страницы
    
    start_idx = page_num * STYLES_PER_PAGE
    end_idx = start_idx + STYLES_PER_PAGE
    current_page_styles = styles_list[start_idx:end_idx]
    
    # Создаём inline-кнопки для стилей на текущей странице (1 в ряд)
    style_buttons = [[InlineKeyboardButton(text=style, callback_data=f"select_style_{style.split('.')[0]}")] for style in current_page_styles]

    # Создаём inline-кнопки навигации
    nav_buttons_row = []
    if total_pages > 1:
        if page_num > 0:
            nav_buttons_row.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"styles_page_{page_num-1}"))
        if page_num < total_pages - 1:
            nav_buttons_row.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"styles_page_{page_num+1}"))
    
    # Объединяем кнопки стилей и навигации
    keyboard_rows = style_buttons
    if nav_buttons_row:
        keyboard_rows.append(nav_buttons_row) # Добавляем строку с навигацией в конец

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
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
        "Теперь пришли мне текст или файл .txt для обработки."
    )
    # Получаем inline-клавиатуру для первой страницы стилей
    styles_keyboard, current_page, total_pages = get_styles_inline_keyboard(0)
    
    await message.answer(welcome_text, reply_markup=get_start_keyboard(), parse_mode='HTML')
    # Отправляем сообщение с выбором стиля и клавиатурой
    style_choice_text = "Выбери, в каком стиле обработать текст:"
    await message.answer(style_choice_text, reply_markup=styles_keyboard)
    if total_pages > 1:
        await message.answer(f"(Стр. {current_page + 1}/{total_pages})")


@dp.callback_query(F.data.startswith("styles_page_")) # Хэндлер для навигации по страницам
async def navigate_styles(call):
    await call.answer() # Отвечаем на callback
    try:
        page_num = int(call.data.split('_')[2])
        styles_keyboard, current_page, total_pages = get_styles_inline_keyboard(page_num)
        # Редактируем сообщение с клавиатурой выбора стиля
        await call.message.edit_text(text="Выбери, в каком стиле обработать текст:", reply_markup=styles_keyboard)
        if total_pages > 1:
            await call.message.answer(f"(Стр. {current_page + 1}/{total_pages})")
    except (IndexError, ValueError):
        await call.message.answer("❌ Ошибка навигации по стилям.")


@dp.callback_query(F.data.startswith("select_style_")) # Хэндлер для выбора стиля
async def select_style(call):
    await call.answer() # Отвечаем на callback
    try:
        # selected_style_id = call.data.split('_')[2] # Старая строка
        # Новая строка: извлекаем всё после "select_style_"
        if call.data.startswith("select_style_"):
            selected_style_id = call.data[len("select_style_"):]
        else:
            # Если формат неожиданный, выбрасываем ошибку
            raise ValueError("Неверный формат callback_data для выбора стиля")

        # Получаем текст из сессии
        user_id = call.from_user.id
        session = session_manager.get_or_create_session(user_id)
        original_text = session.get("original_text", "")
        state = session.get("state", "")

        if not original_text or state != "waiting_for_style":
            await call.message.answer("❌ Стиль выбран, но текст для обработки не найден. Начните сначала.")
            return

        await call.message.answer("Обрабатываю текст... ⏳")
        processed_text = text_processor.process_text_with_style(original_text, selected_style_id)

        # --- Отправка результата ---
        MAX_TELEGRAM_MESSAGE_LENGTH = 4096
        if len(processed_text) > MAX_TELEGRAM_MESSAGE_LENGTH:
            await call.message.answer("Обработанный текст слишком длинный. Отправляю частями...")

            parts = [processed_text[i:i+MAX_TELEGRAM_MESSAGE_LENGTH] for i in range(0, len(processed_text), MAX_TELEGRAM_MESSAGE_LENGTH)]
            for part in parts:
                await call.message.answer(part)
        else:
            await call.message.answer(processed_text)

        # Сбрасываем сессию после ответа
        session_manager.create_session(user_id)
        await call.message.answer("✅ Обработка текста завершена.", reply_markup=get_start_keyboard())

    except (IndexError, ValueError, KeyError) as e: # Добавим KeyError в обработку
        print(f"[ERROR] Ошибка выбора стиля: {e}") # Логируем ошибку
        await call.message.answer("❌ Ошибка выбора стиля. Попробуйте снова или начните сначала.")


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

    # Запоминаем текст из файла и переходим к выбору стиля.
    session_manager.update_session_state(user_id, "waiting_for_style", original_text=original_text)
    # Отправляем inline-клавиатуру стилей для файла
    styles_keyboard, current_page, total_pages = get_styles_inline_keyboard(0)
    style_choice_text = f"Файл загружен ({len(original_text)} символов). Теперь выбери, в каком стиле обработать текст:"
    await message.answer(style_choice_text, reply_markup=styles_keyboard)
    if total_pages > 1:
        await message.answer(f"(Стр. {current_page + 1}/{total_pages})")


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
        # Отправляем inline-клавиатуру стилей для текста
        styles_keyboard, current_page, total_pages = get_styles_inline_keyboard(0)
        style_choice_text = "Теперь выбери, в каком стиле обработать текст:"
        await message.answer(style_choice_text, reply_markup=styles_keyboard)
        if total_pages > 1:
            await message.answer(f"(Стр. {current_page + 1}/{total_pages})")

    # Состояние waiting_for_style теперь обрабатывается через callback_query select_style


# --- Запуск ---
async def main():
    print("Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
