import pyautogui
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


async def screenshot(message: types.Message, user_data: dict = None):
    if user_data is None:
        user_data = {}
    if message.text in ["🏠 Главное меню", "⬅️ Назад", "/cancel"]:
        try:
            from bot import MAIN_COMMAND_BUTTONS
            await message.answer("Возврат в главное меню.", reply_markup=ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True))
        except Exception:
            await message.answer("Возврат в главное меню.")
        return 'CANCELLED'

    screenshot_img = pyautogui.screenshot()
    screenshot_img.save("screenshot.png")
    with open("screenshot.png", "rb") as photo:
        await message.answer_photo(photo)
    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton("🏠 Главное меню"), KeyboardButton("⬅️ Назад")]], resize_keyboard=True)
    await message.answer("Скриншот сделан и отправлен вам!", reply_markup=keyboard)