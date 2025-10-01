import ctypes
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup

async def lock_pc(message: types.Message, user_data: dict = None):
    # allow user to cancel / go back
    if user_data is None:
        user_data = {}
    if message.text in ["🏠 Главное меню", "⬅️ Назад", "/cancel"]:
        try:
            from bot import MAIN_COMMAND_BUTTONS
            await message.answer("Возврат в главное меню.", reply_markup=ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True))
        except Exception:
            await message.answer("Возврат в главное меню.")
        return 'CANCELLED'

    await message.answer("Компьютер заблокирован. 🔒")
    try:
        ctypes.windll.user32.LockWorkStation()
    except Exception as e:
        await message.answer(f"Ошибка блокировки компьютера: {e}")
        print(f"Error locking PC: {e}")
