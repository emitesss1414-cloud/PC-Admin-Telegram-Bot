import subprocess
import re
import os
import getpass
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup

MAC_LIST_FILE = "mac_list.txt"

def get_mac_and_user():
    proc = subprocess.Popen('getmac', stdout=subprocess.PIPE, shell=True)
    out, _ = proc.communicate()
    out = out.decode('cp866')
    macs = re.findall(r'([0-9A-Fa-f]{2}(?:-[0-9A-Fa-f]{2}){5})', out)
    username = getpass.getuser()
    if macs:
        return macs[0], username
    return None, username

def save_mac_to_list(mac, username):
    if not mac:
        return
    entry = f"{mac} | {username}"
    if not os.path.exists(MAC_LIST_FILE):
        with open(MAC_LIST_FILE, "w", encoding="utf-8") as f:
            f.write(entry + "\n")
    else:
        with open(MAC_LIST_FILE, "r", encoding="utf-8") as f:
            entries = [line.strip() for line in f.readlines()]
        if entry not in entries:
            with open(MAC_LIST_FILE, "a", encoding="utf-8") as f:
                f.write(entry + "\n")

def get_all_macs():
    if not os.path.exists(MAC_LIST_FILE):
        return []
    with open(MAC_LIST_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

async def mac_manager(message: types.Message, user_data: dict = None):
    if user_data is None:
        user_data = {}
    if message.text in ["🏠 Главное меню", "⬅️ Назад", "/cancel"]:
        try:
            from bot import MAIN_COMMAND_BUTTONS
            await message.answer("Возврат в главное меню.", reply_markup=ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True))
        except Exception:
            await message.answer("Возврат в главное меню.")
        return 'CANCELLED'

    mac, username = get_mac_and_user()
    save_mac_to_list(mac, username)
    all_macs = get_all_macs()
    text = "MAC-адреса пользователей:\n" + "\n".join(all_macs)
    await message.answer(text)