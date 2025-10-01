import os
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Клавиатура для режима создания папки
CREATE_FOLDER_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("🏠 Главное меню"), KeyboardButton("⬅️ Назад")]]
    ,
    resize_keyboard=True
)

async def create_folder(message, user_data: dict = None):
    if message.text in ["🏠 Главное меню", "⬅️ Назад", "/cancel"]:
        try:
            from bot import MAIN_COMMAND_BUTTONS
            await message.answer("Возврат в главное меню.", reply_markup=__import__('aiogram').types.ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True))
        except Exception:
            await message.answer("Возврат в главное меню.")
        return 'CANCELLED'

    await message.answer(
        "Введите название папки для создания на рабочем столе:",
        reply_markup=CREATE_FOLDER_KEYBOARD
    )

async def create_folder_name(message, user_data: dict = None):
    # Универсальная проверка на отмену
    if message.text in ["🏠 Главное меню", "⬅️ Назад", "/cancel"]:
        return "CANCELLED"

    folder_name = message.text.strip()
    if not folder_name or any(c in folder_name for c in '\/:*?"<>|'):
        await message.answer("Некорректное имя папки. Попробуйте снова.", reply_markup=CREATE_FOLDER_KEYBOARD)
        return None

    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    path = os.path.join(desktop, folder_name)

    if os.path.exists(path):
        await message.answer(f'Папка "{folder_name}" уже существует. Введите другое имя.', reply_markup=CREATE_FOLDER_KEYBOARD)
        return None

    try:
        os.makedirs(path, exist_ok=True)
        await message.answer(f'✅ Папка "{folder_name}" создана!\n\nВведите ещё имя для новой папки или вернитесь в меню.', reply_markup=CREATE_FOLDER_KEYBOARD)
    except Exception as e:
        await message.answer(f"⛔ Ошибка создания папки: {e}", reply_markup=CREATE_FOLDER_KEYBOARD)
        return "CANCELLED"
    return None