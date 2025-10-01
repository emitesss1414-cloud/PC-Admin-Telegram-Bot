import os
import pyautogui
import pygetwindow as gw
import pygetwindow
import asyncio
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

YOUTUBE_BUTTONS = [
    [KeyboardButton("🏠 Главное меню")],
    [KeyboardButton("⬅️ Назад")]
]

YOUTUBE_CONTROL_BUTTONS = [
    [KeyboardButton("⏯️ Пауза/Воспр."), KeyboardButton("⏩ Вперёд 5с"), KeyboardButton("⏪ Назад 5с")],
    [KeyboardButton("🔊 Громче"), KeyboardButton("🔉 Тише")],
    [KeyboardButton("🔲 Полный экран"), KeyboardButton("🔳 Обычный режим")],
    [KeyboardButton("⏹️ Стоп"), KeyboardButton("🏠 Главное меню")]
]

def get_youtube_windows():
    return [w for w in gw.getAllTitles() if 'youtube' in w.lower()]

async def youtube(message: types.Message, user_data: dict = None):
    if user_data is None:
        user_data = {}
    user_data['youtube_mode'] = True
    youtube_windows = get_youtube_windows()
    keyboard = ReplyKeyboardMarkup(keyboard=YOUTUBE_BUTTONS, resize_keyboard=True)

    if youtube_windows:
        msg = "Открытые вкладки YouTube:\n" + "\n".join(f"{i+1}. {w}" for i, w in enumerate(youtube_windows))
        msg += "\n\nВведите номер вкладки для управления или отправьте ссылку для открытия нового видео."
        user_data['youtube_tabs'] = youtube_windows
    else:
        msg = "Нет открытых вкладок YouTube. Отправьте ссылку для открытия нового видео."
        user_data['youtube_tabs'] = []
    
    await message.answer(msg, reply_markup=keyboard)

async def youtube_link(message: types.Message, user_data: dict = None):
    if user_data is None:
        user_data = {}
    text = message.text.strip()
    keyboard = ReplyKeyboardMarkup(keyboard=YOUTUBE_BUTTONS, resize_keyboard=True)
    control_keyboard = ReplyKeyboardMarkup(keyboard=YOUTUBE_CONTROL_BUTTONS, resize_keyboard=True)

    # Обработка выхода/отмены
    if text in ["🏠 Главное меню", "⬅️ Назад", "/cancel"]:
        user_data.pop('youtube_mode', None)
        user_data.pop('youtube_tabs', None)
        user_data.pop('youtube_control_window', None)
        from bot import MAIN_COMMAND_BUTTONS
        await message.answer("Выход из управления YouTube.", reply_markup=ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True))
        return 'CANCELLED'

    if text.isdigit() and user_data.get('youtube_tabs'):
        idx = int(text) - 1
        tabs = user_data.get('youtube_tabs', [])
        if 0 <= idx < len(tabs):
            try:
                win = gw.getWindowsWithTitle(tabs[idx])[0]
                win.activate()
                user_data['youtube_control_window'] = tabs[idx]
                await message.answer(f"Вкладка активирована: {tabs[idx]}", reply_markup=control_keyboard)
            except (IndexError, pygetwindow.PyGetWindowException) as e:
                await message.answer(f"Не удалось активировать окно: {e}", reply_markup=keyboard)
        else:
            await message.answer("Некорректный номер вкладки.", reply_markup=keyboard)
        return

    if "youtube.com" in text or "youtu.be" in text:
        os.system(f'start "" "{text}"')
        await message.answer("Видео открыто! Теперь вы можете выбрать его из списка для управления.", reply_markup=keyboard)
        await youtube(message, user_data) # Refresh list
    else:
        await message.answer("Пожалуйста, отправьте корректную ссылку на YouTube или выберите вкладку.", reply_markup=keyboard)

async def youtube_control(message: types.Message, user_data: dict = None):
    if user_data is None:
        user_data = {}
    text = message.text
    control_keyboard = ReplyKeyboardMarkup(keyboard=YOUTUBE_CONTROL_BUTTONS, resize_keyboard=True)
    window_title = user_data.get('youtube_control_window')

    # Обработка выхода/отмены
    if text in ["🏠 Главное меню", "⬅️ Назад", "/cancel"]:
        user_data.pop('youtube_mode', None)
        user_data.pop('youtube_tabs', None)
        user_data.pop('youtube_control_window', None)
        from bot import MAIN_COMMAND_BUTTONS
        await message.answer("Выход из управления YouTube.", reply_markup=ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True))
        return 'CANCELLED'

    if not window_title:
        await message.answer("Сначала выберите вкладку для управления.", reply_markup=YOUTUBE_BUTTONS)
        user_data.clear()
        return
        
    try:
        win = gw.getWindowsWithTitle(window_title)[0]
        win.activate()
    except (IndexError, pygetwindow.PyGetWindowException):
        await message.answer("Окно YouTube больше не найдено. Выберите другую вкладку.", reply_markup=YOUTUBE_BUTTONS)
        user_data.clear()
        return

    command_map = {
        "⏯️ Пауза/Воспр.": "space",
        "⏩ Вперёд 5с": "right",
        "⏪ Назад 5с": "left",
        "🔊 Громче": "up",
        "🔉 Тише": "down",
        "🔲 Полный экран": "f",
        "🔳 Обычный режим": "esc",
        "⏹️ Стоп": "k"
    }

    if text in command_map:
        pyautogui.press(command_map[text])
        await message.answer(f"Команда '{text}' выполнена.", reply_markup=control_keyboard)
    else:
        await message.answer("Неизвестная команда.", reply_markup=control_keyboard)
