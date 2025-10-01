import os
from aiogram import types

async def shutdown(message: types.Message, user_data: dict = None):
    if user_data is None:
        user_data = {}
    if message.text in ["🏠 Главное меню", "⬅️ Назад", "/cancel"]:
        try:
            from bot import MAIN_COMMAND_BUTTONS
            await message.answer("Отмена.", reply_markup=types.ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True))
        except Exception:
            await message.answer("Отмена.")
        return 'CANCELLED'

    await message.answer("Компьютер выключается...")
    os.system("shutdown /s /t 1")