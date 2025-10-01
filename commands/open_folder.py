import os
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Клавиатура для режима открытия папки
OPEN_FOLDER_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("🏠 Главное меню"), KeyboardButton("⬅️ Назад")]
    ],
    resize_keyboard=True
)

async def open_folder(message, user_data: dict = None):
    await message.answer(
        "Введите полный путь к папке, которую нужно открыть:",
        reply_markup=OPEN_FOLDER_KEYBOARD
    )

async def open_folder_path(message, user_data: dict = None):
    if user_data is None:
        user_data = {}
    if message.text in ["🏠 Главное меню", "⬅️ Назад", "/cancel"]:
        return "CANCELLED"

    path = message.text.strip()
    if not os.path.isdir(path):
        await message.answer("⛔ Папка не найдена. Проверьте путь и попробуйте снова.", reply_markup=OPEN_FOLDER_KEYBOARD)
        return None
    
    try:
        os.startfile(path)
        await message.answer(f"✅ Папка {path} открыта.\n\nМожете ввести другой путь или вернуться в меню.", reply_markup=OPEN_FOLDER_KEYBOARD)
    except Exception as e:
        await message.answer(f"⛔ Ошибка открытия папки: {e}", reply_markup=OPEN_FOLDER_KEYBOARD)
        return "CANCELLED"
    return None