import os
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup


async def reboot(message: types.Message, user_data: dict = None):
    if user_data is None:
        user_data = {}
    if message.text in ["🏠 Главное меню", "⬅️ Назад", "/cancel"]:
        try:
            from bot import MAIN_COMMAND_BUTTONS
            await message.answer("Отмена.", reply_markup=ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True))
        except Exception:
            await message.answer("Отмена.")
        return 'CANCELLED'

    await message.answer("Компьютер перезагружается...")
    os.system("shutdown /r /t 1")