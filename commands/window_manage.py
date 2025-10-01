from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import pygetwindow as gw
import win32gui
import win32con

WINDOW_MANAGE_BUTTONS = [
    [KeyboardButton("Список окон"), KeyboardButton("Свернуть окно"), KeyboardButton("Закрыть окно")],
    [KeyboardButton("Переключить окно"), KeyboardButton("⬅️ Назад"), KeyboardButton("🏠 Главное меню")]
]

async def window_manage(message: types.Message, user_data: dict = None):
    # allow cancel/back at any time
    if message.text in ["🏠 Главное меню", "⬅️ Назад", "/cancel"]:
        try:
            from bot import MAIN_COMMAND_BUTTONS
            await message.answer("Возврат в главное меню.", reply_markup=ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True))
        except Exception:
            await message.answer("Возврат в главное меню.")
        if isinstance(user_data, dict):
            user_data.clear()
        return

    keyboard = ReplyKeyboardMarkup(keyboard=WINDOW_MANAGE_BUTTONS, resize_keyboard=True)
    await message.answer(
        "Управление окнами:\nВыберите действие. Для возврата используйте '⬅️ Назад' или '🏠 Главное меню'.",
        reply_markup=keyboard
    )

async def window_action(message: types.Message, user_data: dict = None):
    if user_data is None:
        user_data = {}
    text = message.text.strip()
    keyboard = ReplyKeyboardMarkup(keyboard=WINDOW_MANAGE_BUTTONS, resize_keyboard=True)

    if text in ["🏠 Главное меню", "⬅️ Назад", "/cancel"]:
        user_data.clear()
        await message.answer("Отмена управления окнами.")
        return

    if text == "Список окон":
        try:
            windows = [w for w in gw.getAllTitles() if w.strip()]
            if windows:
                msg = "Открытые окна:\n" + "\n".join(f"{i+1}. {w}" for i, w in enumerate(windows))
            else:
                msg = "Нет открытых окон."
        except Exception as e:
            msg = f"Не удалось получить список окон: {e}"
            print(f"Error getting window list: {e}")
        await message.answer(msg, reply_markup=keyboard)

    elif text == "Свернуть окно":
        try:
            win = gw.getActiveWindow()
            if win:
                win.minimize()
                await message.answer("Активное окно свернуто.", reply_markup=keyboard)
            else:
                await message.answer("Нет активного окна.", reply_markup=keyboard)
        except Exception as e:
            await message.answer(f"Ошибка: {e}", reply_markup=keyboard)
            print(f"Error minimizing window: {e}")

    elif text == "Закрыть окно":
        try:
            win = gw.getActiveWindow()
            if win:
                win.close()
                await message.answer("Активное окно закрыто.", reply_markup=keyboard)
            else:
                await message.answer("Нет активного окна.", reply_markup=keyboard)
        except Exception as e:
            await message.answer(f"Ошибка: {e}", reply_markup=keyboard)
            print(f"Error closing window: {e}")

    elif text == "Переключить окно":
        try:
            windows = [w for w in gw.getAllTitles() if w.strip()]
            if not windows:
                await message.answer("Нет окон для переключения.", reply_markup=keyboard)
                return
            user_data['window_switch_list'] = windows
            user_data['window_switch'] = True
            msg = "Введите номер окна для активации:\n" + "\n".join(f"{i+1}. {w}" for i, w in enumerate(windows))
            await message.answer(msg, reply_markup=keyboard)
        except Exception as e:
            await message.answer(f"Ошибка: {e}", reply_markup=keyboard)
            print(f"Error preparing to switch window: {e}")

    elif user_data.get('window_switch') and text.isdigit():
        windows = user_data.get('window_switch_list', [])
        try:
            idx = int(text) - 1
            if 0 <= idx < len(windows):
                win = gw.getWindowsWithTitle(windows[idx])[0]
                hwnd = win._hWnd
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                win32gui.BringWindowToTop(hwnd)
                await message.answer(f"Окно '{windows[idx]}' активировано и поднято поверх всех.", reply_markup=keyboard)
            else:
                await message.answer("Некорректный номер окна.", reply_markup=keyboard)
        except Exception as e:
            await message.answer(f"Ошибка переключения окна: {e}", reply_markup=keyboard)
            print(f"Error switching window: {e}")
        # Reset the switch mode after an attempt
        user_data['window_switch'] = False
        user_data.pop('window_switch_list', None)
    
    else:
        await message.answer("Неизвестная команда для управления окнами.", reply_markup=keyboard)
