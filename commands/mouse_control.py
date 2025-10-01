import asyncio
import pyautogui
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton



MOUSE_BUTTONS = [
    [KeyboardButton("⬆️")],
    [KeyboardButton("⬅️"), KeyboardButton("ЛКМ"), KeyboardButton("ПКМ"), KeyboardButton("➡️")],
    [KeyboardButton("⬇️")],
    [KeyboardButton("Колесо ↑"), KeyboardButton("Колесо ↓")],
    [KeyboardButton("Стоп движение"), KeyboardButton("⬅️ Назад"), KeyboardButton("🏠 Главное меню")]
]

FILES_BUTTONS = [
    [KeyboardButton("🏠 Главное меню")],
    [KeyboardButton("⬅️ Назад")]
]

async def move_mouse_loop(user_data: dict):
    direction = user_data.get('mouse_direction')
    if not direction:
        return

    while user_data.get('mouse_moving'):
        if direction == "⬆️":
            pyautogui.moveRel(0, -20)
        elif direction == "⬇️":
            pyautogui.moveRel(0, 20)
        elif direction == "⬅️":
            pyautogui.moveRel(-20, 0)
        elif direction == "➡️":
            pyautogui.moveRel(20, 0)
        await asyncio.sleep(0.05)

async def mouse_control(message: types.Message, user_data: dict = None):
    if user_data is None:
        user_data = {}
    user_data['mouse_control_mode'] = True
    keyboard = ReplyKeyboardMarkup(keyboard=MOUSE_BUTTONS, resize_keyboard=True)
    await message.answer(
        "Управление мышью:\nИспользуйте кнопки для перемещения и кликов.",
        reply_markup=keyboard
    )

async def mouse_action(message: types.Message, user_data: dict = None):
    if user_data is None:
        user_data = {}
    action = message.text
    keyboard = ReplyKeyboardMarkup(keyboard=MOUSE_BUTTONS, resize_keyboard=True)

    if message.text in ["🏠 Главное меню", "⬅️ Назад", "/cancel"]:
        user_data.clear()
        await message.answer("Отмена управления мышью.", reply_markup=FILES_BUTTONS)
        return 'CANCELLED'

    if action in ["⬆️", "⬇️", "⬅️", "➡️"]:
        if user_data.get('mouse_moving'):
            user_data['mouse_moving'] = False
            await asyncio.sleep(0.1) # give time for the loop to stop

        user_data['mouse_moving'] = True
        user_data['mouse_direction'] = action
        asyncio.create_task(move_mouse_loop(user_data))
        await message.answer(f"Движение мыши '{action}' начато. Для остановки нажмите 'Стоп движение'.", reply_markup=keyboard)
    
    elif action == "Стоп движение":
        if user_data.get('mouse_moving'):
            user_data['mouse_moving'] = False
            await message.answer("Движение мыши остановлено.", reply_markup=keyboard)
        else:
            await message.answer("Мышь не двигается.", reply_markup=keyboard)

    elif action == "ЛКМ":
        pyautogui.click(button='left')
        await message.answer("ЛКМ клик.", reply_markup=keyboard)
    elif action == "ПКМ":
        pyautogui.click(button='right')
        await message.answer("ПКМ клик.", reply_markup=keyboard)
    elif action == "Колесо ↑":
        pyautogui.scroll(100)
        await message.answer("Колесо вверх.", reply_markup=keyboard)
    elif action == "Колесо ↓":
        pyautogui.scroll(-100)
        await message.answer("Колесо вниз.", reply_markup=keyboard)
    else:
        await message.answer("Неизвестная команда.", reply_markup=keyboard)