
import os
from aiogram import types

# Папка для временных скринов
TEMP_SCREEN_PATH = os.path.join(os.path.dirname(__file__), 'temp_screen.png')

async def screencast(message: types.Message, user_data: dict = None):
	# allow user to cancel / go back
	if message.text in ["🏠 Главное меню", "⬅️ Назад", "/cancel"]:
		try:
			from bot import MAIN_COMMAND_BUTTONS
			await message.answer("Возврат в главное меню.", reply_markup=types.ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True))
		except Exception:
			await message.answer("Возврат в главное меню.")
		return 'CANCELLED'

	await message.answer("Функция скринкаста пока не реализована.")
