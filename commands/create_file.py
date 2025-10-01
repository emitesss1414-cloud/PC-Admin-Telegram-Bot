import os
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Клавиатура для режима создания файла
CREATE_FILE_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("🏠 Главное меню"), KeyboardButton("⬅️ Назад")]
    ],
    resize_keyboard=True
)

async def create_file(message, user_data: dict = None):
    if message.text in ["🏠 Главное меню", "⬅️ Назад", "/cancel"]:
        try:
            from bot import MAIN_COMMAND_BUTTONS
            await message.answer("Возврат в главное меню.", reply_markup=__import__('aiogram').types.ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True))
        except Exception:
            await message.answer("Возврат в главное меню.")
        return 'CANCELLED'

    await message.answer(
        "Введите имя файла для создания на рабочем столе:",
        reply_markup=CREATE_FILE_KEYBOARD
    )

async def create_file_name(message, user_data: dict = None):
    if message.text in ["🏠 Главное меню", "⬅️ Назад", "/cancel"]:
        return "CANCELLED"

    file_name = message.text.strip()
    if not file_name or any(c in file_name for c in '\/:*?"<>|'):
        await message.answer("Некорректное имя файла. Попробуйте снова.", reply_markup=CREATE_FILE_KEYBOARD)
        return None

    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    path = os.path.join(desktop, file_name)

    if os.path.exists(path):
        await message.answer(f'Файл "{file_name}" уже существует. Введите другое имя.', reply_markup=CREATE_FILE_KEYBOARD)
        return None

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("")
        await message.answer(f'✅ Файл "{file_name}" создан!\n\nВведите ещё имя для нового файла или вернитесь в меню.', reply_markup=CREATE_FILE_KEYBOARD)
    except Exception as e:
        await message.answer(f"⛔ Ошибка создания файла: {e}", reply_markup=CREATE_FILE_KEYBOARD)
        return "CANCELLED"
    return None