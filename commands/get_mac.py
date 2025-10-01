
import os
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup

MAC_RESULT_PATH = r"C:\Users\ПК\Desktop\PC-Admin-Bot-1111\мак адресса\dist\mac_result.txt"

async def get_mac(message: types.Message, user_data: dict = None):
    if user_data is None:
        user_data = {}
    if message.text in ["🏠 Главное меню", "⬅️ Назад", "/cancel"]:
        try:
            from bot import MAIN_COMMAND_BUTTONS
            await message.answer("Возврат в главное меню.", reply_markup=ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True))
        except Exception:
            await message.answer("Возврат в главное меню.")
        return 'CANCELLED'

    if os.path.exists(MAC_RESULT_PATH):
        with open(MAC_RESULT_PATH, "r", encoding="utf-8") as f:
            text = f.read()
        # Если файл большой, отправить как документ
        if len(text) > 3500:
            await message.answer_document(document=open(MAC_RESULT_PATH, "rb"), filename="mac_result.txt")
        else:
            await message.answer(text)
    else:
        await message.answer("Файл с MAC-адресами не найден.")