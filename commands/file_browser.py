import os
import string
from aiogram.types import ReplyKeyboardMarkup

def get_available_drives() -> list[str]:
    """Возвращает список доступных дисков в системе (C:, D: и т.д.)."""
    drives = []
    for letter in string.ascii_uppercase:
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            drives.append(drive)
    return drives

def get_directory_contents(path: str) -> dict:
    """
    Получает содержимое директории, разделенное на папки и файлы.
    Возвращает словарь {'dirs': [...], 'files': [...]}.
    """
    dirs = []
    files = []
    try:
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_dir():
                    dirs.append(entry.name)
                else:
                    files.append(entry.name)
        return {"dirs": sorted(dirs), "files": sorted(files)}
    except (PermissionError, FileNotFoundError):
        return None # Возвращаем None в случае ошибки доступа или если путь не найден


async def file_browser_handler(message, user_data: dict = None):
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

    drives = get_available_drives()
    if not drives:
        await message.answer("Диски не найдены или недоступны.")
        return

    await message.answer("Доступные диски: " + ", ".join(drives))

