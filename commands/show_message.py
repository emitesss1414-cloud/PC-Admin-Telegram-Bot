import ctypes
import threading
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Клавиатура для режима отображения сообщения
SHOW_MESSAGE_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("🏠 Главное меню"), KeyboardButton("⬅️ Назад")]
    ],
    resize_keyboard=True
)

def show_windows_messagebox(text):
    ctypes.windll.user32.MessageBoxW(0, text, "Сообщение от администратора", 0x40 | 0x1000) # MB_ICONINFORMATION | MB_SYSTEMMODAL

async def show_message(message, user_data: dict = None):
    await message.answer(
        "Введите текст сообщения для отображения на экране:",
        reply_markup=SHOW_MESSAGE_KEYBOARD
    )

async def show_message_text(message, user_data: dict = None):
    if message.text in ["🏠 Главное меню", "⬅️ Назад", "/cancel"]:
        return "CANCELLED"

    text = message.text.strip()
    if not text:
        await message.answer("Сообщение не может быть пустым. Попробуйте снова.", reply_markup=SHOW_MESSAGE_KEYBOARD)
        return None

    try:
        # run the blocking MessageBox in a background thread so the bot isn't blocked
        threading.Thread(target=show_windows_messagebox, args=(text,), daemon=True).start()
        # immediately return user to main menu keyboard so they can continue
        try:
            from bot import MAIN_COMMAND_BUTTONS
            await message.answer(f"✅ Сообщение отправлено на экран: \"{text}\"", reply_markup=ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True))
        except Exception:
            await message.answer(f"✅ Сообщение отправлено на экран: \"{text}\"")
        return 'CANCELLED'
    except Exception as e:
        try:
            from bot import MAIN_COMMAND_BUTTONS
            await message.answer(f"⛔ Ошибка при показе сообщения: {e}", reply_markup=ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True))
        except Exception:
            await message.answer(f"⛔ Ошибка при показе сообщения: {e}")
        return 'CANCELLED'