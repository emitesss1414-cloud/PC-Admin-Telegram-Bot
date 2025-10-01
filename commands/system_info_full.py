import os
import psutil
import getpass
import socket
import platform
from aiogram import types

def get_gpu_info():
    # This is a placeholder. Getting GPU info on Windows without external libraries is complex.
    # We can try to parse dxdiag output, but it's not ideal.
    # For now, we will return a placeholder.
    return "Не удалось определить"

async def system_info_full(message: types.Message, user_data: dict = None):
    if user_data is None:
        user_data = {}
    # allow user to cancel / go back at any time
    if message.text in ["🏠 Главное меню", "⬅️ Назад", "/cancel"]:
        try:
            from bot import MAIN_COMMAND_BUTTONS
            await message.answer("Возврат в главное меню.", reply_markup=types.ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True))
        except Exception:
            await message.answer("Возврат в главное меню.")
        return 'CANCELLED'

    user = getpass.getuser()
    hostname = socket.gethostname()
    os_name = platform.system()
    os_version = platform.version()
    cpu = platform.processor()
    ram = round(psutil.virtual_memory().total / (1024**3), 2)
    disk_path = os.path.abspath(os.sep)
    disk = round(psutil.disk_usage(disk_path).total / (1024**3), 2)
    arch = platform.architecture()[0]
    gpu = get_gpu_info()
    model = f"{platform.system()} {platform.machine()}"

    info = (
        "🖥️ <b>Информация о ПК</b>\n\n"
        f"💻 <b>Имя устройства:</b> <code>{hostname}</code>\n"
        f"🏷️ <b>Модель устройства:</b> <code>{model}</code>\n"
        f"👤 <b>Пользователь:</b> <code>{user}</code>\n"
        f"🖥️ <b>ОС:</b> <code>{os_name} ({os_version})</code>\n"
        f"🧠 <b>Процессор:</b> <code>{cpu}</code>\n"
        f"🎮 <b>Видеокарта:</b> <code>{gpu}</code>\n"
    f"💾 <b>ОЗУ:</b> <code>{ram} ГБ</code>\n"
    f"🗄️ <b>Диск ({disk_path}):</b> <code>{disk} ГБ</code>\n"
        f"🔢 <b>Тип системы:</b> <code>{arch}</code>\n"
    )
    await message.answer(info, parse_mode="HTML")
