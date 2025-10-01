import os
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

FILES_BUTTONS = [
    [KeyboardButton("🏠 Главное меню")],
    [KeyboardButton("⬅️ Назад")]
]

ACTION_KEYBOARD = [
    [KeyboardButton("Открыть"), KeyboardButton("Удалить"), KeyboardButton("Переименовать")],
    [KeyboardButton("⬅️ Назад"), KeyboardButton("🏠 Главное меню")]
]

def get_desktop_path():
    return os.path.join(os.path.expanduser("~"), "Desktop")

async def files_on_desktop(message: types.Message, user_data: dict = None):
    # preserve caller dict when an empty dict is passed (empty dict is falsy),
    # so only replace when user_data is truly None
    if user_data is None:
        user_data = {}
    if message.text in ["🏠 Главное меню", "⬅️ Назад", "/cancel"]:
        try:
            from bot import MAIN_COMMAND_BUTTONS
            await message.answer(
                "Возврат в главное меню.",
                reply_markup=ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True)
            )
        except Exception:
            await message.answer("Возврат в главное меню.")
        return

    desktop = get_desktop_path()
    try:
        files = [f for f in os.listdir(desktop) if os.path.isfile(os.path.join(desktop, f))]
    except FileNotFoundError:
        await message.answer("Рабочий стол не найден.")
        return

    keyboard = ReplyKeyboardMarkup(keyboard=FILES_BUTTONS, resize_keyboard=True)
    if not files:
        await message.answer("На рабочем столе нет файлов.", reply_markup=keyboard)
        return

    user_data['desktop_files_list'] = files
    user_data['desktop_files_mode'] = True

    msg = "Файлы на рабочем столе:\n" + "\n".join(f"{i+1}. {f}" for i, f in enumerate(files))
    msg += "\n\nВведите номер файла для выбора действия."
    await message.answer(msg, reply_markup=keyboard)

async def files_on_desktop_action(message: types.Message, user_data: dict = None):
    # preserve caller dict when an empty dict is passed
    if user_data is None:
        user_data = {}
    text = message.text.strip()
    keyboard = ReplyKeyboardMarkup(keyboard=FILES_BUTTONS, resize_keyboard=True)
    action_keyboard = ReplyKeyboardMarkup(keyboard=ACTION_KEYBOARD, resize_keyboard=True)
    desktop = get_desktop_path()

    if text == "🏠 Главное меню":
        user_data.clear()
        from bot import MAIN_COMMAND_BUTTONS
        await message.answer(
            "Главное меню:",
            reply_markup=ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True)
        )
        return
    if text in ["⬅️ Назад", "/cancel"]:
        user_data.clear()
        await message.answer("Отмена работы с файлами на рабочем столе.", reply_markup=keyboard)
        return

    # State: waiting for new name
    if user_data.get('await_new_name'):
        selected_file = user_data.get('selected_file_path')
        if not selected_file or not os.path.exists(selected_file):
            await message.answer("Файл не найден. Пожалуйста, начните заново.", reply_markup=keyboard)
            user_data.clear()
            return

        new_name = text
        new_path = os.path.join(desktop, new_name)

        if any(c in new_name for c in '\/:*?"<>|'):
            await message.answer("Некорректное имя файла. Попробуйте снова.", reply_markup=keyboard)
            return

        if os.path.exists(new_path):
            await message.answer("Файл с таким именем уже существует.", reply_markup=keyboard)
            return

        try:
            os.rename(selected_file, new_path)
            await message.answer("Файл переименован!", reply_markup=keyboard)
        except Exception as e:
            await message.answer(f"Ошибка переименования: {e}", reply_markup=keyboard)
        
        user_data.pop('await_new_name', None)
        user_data.pop('selected_file_path', None)
        await files_on_desktop(message, user_data) # Show the list again
        return

    # State: file selected, waiting for action
    if user_data.get('selected_file_path'):
        selected_file = user_data.get('selected_file_path')
        if not os.path.exists(selected_file):
            await message.answer("Выбранный файл больше не существует. Обновите список.", reply_markup=keyboard)
            user_data.clear()
            return
            
        if text == "Открыть":
            try:
                os.startfile(selected_file)
                await message.answer("Файл открыт!", reply_markup=action_keyboard)
            except Exception as e:
                await message.answer(f"Ошибка открытия файла: {e}", reply_markup=action_keyboard)
        elif text == "Удалить":
            try:
                os.remove(selected_file)
                await message.answer("Файл удалён!", reply_markup=keyboard)
                user_data.clear()
                await files_on_desktop(message, user_data) # Refresh list
            except Exception as e:
                await message.answer(f"Ошибка удаления файла: {e}", reply_markup=action_keyboard)
        elif text == "Переименовать":
            user_data['await_new_name'] = True
            await message.answer("Введите новое имя файла:", reply_markup=keyboard)
        else:
            await message.answer("Выберите действие из предложенных.", reply_markup=action_keyboard)
        return

    # State: initial, waiting for file number
    if text.isdigit():
        files = user_data.get('desktop_files_list', [])
        try:
            idx = int(text) - 1
            if 0 <= idx < len(files):
                file_name = files[idx]
                file_path = os.path.join(desktop, file_name)
                if os.path.exists(file_path):
                    user_data['selected_file_path'] = file_path
                    await message.answer(f"Выбран файл: {file_name}\nВыберите действие.", reply_markup=action_keyboard)
                else:
                    await message.answer("Файл больше не существует. Обновите список.", reply_markup=keyboard)
                    user_data.clear()
            else:
                await message.answer("Некорректный номер файла.", reply_markup=keyboard)
        except (ValueError, IndexError):
            await message.answer("Некорректный ввод. Введите номер файла.", reply_markup=keyboard)
        return

    await message.answer("Неизвестная команда. Введите номер файла или используйте кнопки.", reply_markup=keyboard)