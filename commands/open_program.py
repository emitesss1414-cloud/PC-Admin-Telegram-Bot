import os
import subprocess
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Пути к программам (рекомендуется вынести в конфиг)
PROGRAM_PATHS = {
    "steam": r"C:\Program Files (x86)\Steam\steam.exe",
    "discord": r"%LOCALAPPDATA%\Discord\Update.exe --processStart Discord.exe",
    "google chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "telegram desktop": r"%APPDATA%\Telegram Desktop\Telegram.exe",
    "проводник": "explorer",
    "диспетчер задач": "taskmgr"
}

# Клавиатура для режима открытия программ
OPEN_PROGRAM_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("Steam"), KeyboardButton("Discord"), KeyboardButton("Google Chrome")],
        [KeyboardButton("Telegram Desktop"), KeyboardButton("Проводник"), KeyboardButton("Диспетчер задач")],
        [KeyboardButton("🏠 Главное меню"), KeyboardButton("⬅️ Назад")]
    ],
    resize_keyboard=True
)

async def open_program(message, user_data: dict = None):
    await message.answer(
        "Выберите программу для запуска, введите ее имя или полный путь:",
        reply_markup=OPEN_PROGRAM_KEYBOARD
    )

async def open_program_name(message, user_data: dict = None):
    if user_data is None:
        user_data = {}
    if message.text in ["🏠 Главное меню", "⬅️ Назад", "/cancel"]:
        return "CANCELLED"

    program_name = message.text.strip().lower()
    path_to_open = None

    if program_name in PROGRAM_PATHS:
        path_to_open = PROGRAM_PATHS[program_name]
    elif os.path.isfile(program_name) and program_name.endswith(('.exe', '.lnk')):
        path_to_open = program_name

    if path_to_open:
        try:
            # Раскрываем переменные окружения (например, %LOCALAPPDATA%)
            expanded_path = os.path.expandvars(path_to_open)
            subprocess.Popen(expanded_path, shell=True)
            await message.answer(f"✅ Программа '{program_name.title()}' запущена.", reply_markup=OPEN_PROGRAM_KEYBOARD)
        except Exception as e:
            await message.answer(f"⛔ Ошибка запуска программы: {e}", reply_markup=OPEN_PROGRAM_KEYBOARD)
            return "CANCELLED"
    else:
        await message.answer("Не удалось найти программу. Попробуйте ввести ее полное имя (например, `chrome`) или укажите путь к .exe файлу.", reply_markup=OPEN_PROGRAM_KEYBOARD)
    
    return None