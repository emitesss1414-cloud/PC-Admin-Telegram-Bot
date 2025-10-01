
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


async def play_music(message: types.Message, user_data: dict = None):
	if user_data is None:
		user_data = {}
	if message.text in ["🏠 Главное меню", "⬅️ Назад", "/cancel"]:
		try:
			from bot import MAIN_COMMAND_BUTTONS
			await message.answer("Возврат в главное меню.", reply_markup=ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True))
		except Exception:
			await message.answer("Возврат в главное меню.")
		return 'CANCELLED'

	keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton("🏠 Главное меню"), KeyboardButton("⬅️ Назад")]], resize_keyboard=True)
	await message.answer("Функция воспроизведения музыки пока не реализована.", reply_markup=keyboard)
