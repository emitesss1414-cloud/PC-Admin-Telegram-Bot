import os
import psutil
from aiogram import types


async def system_info(message: types.Message, user_data: dict = None):
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

    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk_path = os.path.abspath(os.sep)
    disk = psutil.disk_usage(disk_path).percent
    net = psutil.net_io_counters()

    await message.answer(
        f"💻 Системная информация:\n"
        f"CPU: {cpu}%\n"
        f"RAM: {ram}%\n"
        f"Диск ({disk_path}): {disk}%\n"
        f"Сеть: отправлено {net.bytes_sent // 1024 // 1024} МБ, получено {net.bytes_recv // 1024 // 1024} МБ"
    )