import asyncio
import math
import os
import time

import bcrypt
import inspect
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils import executor
from dotenv import load_dotenv

# Импорт всех команд
from commands.create_file import create_file, create_file_name
from commands.create_folder import create_folder, create_folder_name
from commands.files_on_desktop import files_on_desktop, files_on_desktop_action
from commands.get_mac import get_mac
from commands.installed_apps import get_installed_apps
from commands.ip_info import get_private_ip, get_public_ip
from commands.lock_pc import lock_pc
from commands.mouse_control import mouse_control, mouse_action
from commands.open_folder import open_folder, open_folder_path
from commands.open_program import open_program, open_program_name
from commands.open_site import open_site, open_site_link
from commands.performance_graphs import generate_performance_graphs
from commands.play_music import play_music
# removed power management functions (modes removed)
from commands.quick_access import FOLDER_PATHS, quick_access_initial, handle_quick_access_choice
from commands.reboot import reboot
from commands.screenshot import screenshot
from commands.set_brightness import set_brightness, set_brightness_value
from commands.set_volume import set_volume, set_volume_value
from commands.show_message import show_message, show_message_text
from commands.shutdown import shutdown
from commands.system_info import system_info
from commands.system_info_full import system_info_full

from commands.theme_changer import set_theme, theme_changer_handler
from commands.wallpaper_changer import set_wallpaper
from commands.window_manage import window_manage, window_action
from commands.youtube import youtube, youtube_control, youtube_link
from commands.task_manager import kill_process_by_pid, get_process_list, task_manager_handler
from commands.file_browser import get_available_drives, get_directory_contents
from utils.fb_tokens import add_token, resolve_token, cleanup, clear_user, FB_TOKEN_TTL
FB_TOKEN_TTL = 300  # seconds


async def call_handler(handler, message, user_data):
    """Call handler which may accept (message) or (message, user_data).
    Uses signature inspection to decide how to call coroutine or regular function.
    """
    wants_userdata = False
    try:
        sig = inspect.signature(handler)
        params = [p for p in sig.parameters.values() if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
        # Only pass user_data when the handler explicitly declares the second parameter named 'user_data'.
        if len(params) >= 2 and params[1].name == 'user_data':
            wants_userdata = True
    except Exception:
        # fallback: assume it accepts only message
        wants_userdata = False

    res = None
    if asyncio.iscoroutinefunction(handler):
        if wants_userdata:
            res = await handler(message, user_data)
        else:
            res = await handler(message)
    else:
        if wants_userdata:
            res = handler(message, user_data)
        else:
            res = handler(message)

    # If handler returned a dict, assume it's a new user_data snapshot and merge it
    try:
        if isinstance(res, dict) and isinstance(user_data, dict):
            # replace contents of the per-user dict to preserve identity
            user_data.clear()
            user_data.update(res)
    except Exception:
        pass

    return res


# token map helpers are provided by utils.fb_tokens

load_dotenv()

# --- Константы и настройки ---
TOKEN = os.getenv("TOKEN")
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID"))
MAC_ADDRESS = os.getenv("WOL_MAC_ADDRESS")
# Получаем список хэшей из .env, разделённых запятой, и преобразуем каждый в bytes
BOT_PASSWORD_HASHES = [h.strip().encode("utf-8") for h in os.getenv("BOT_PASSWORD_HASHES", "").split(",") if h.strip()]

MAX_LOGIN_ATTEMPTS = 3
LOCKOUT_DURATION = 600
PROCESS_LIST_PAGE_SIZE = 10
APPS_PAGE_SIZE = 15

# --- Клавиатуры ---
MAIN_COMMAND_BUTTONS = [
    [KeyboardButton("⏻ Выключить ПК"), KeyboardButton("🔄 Перезагрузить ПК")],
    [KeyboardButton("📂 Создать папку"), KeyboardButton("📄 Создать файл")],
    [KeyboardButton("🖥️ Открыть программу"), KeyboardButton("▶️ YouTube видео")],
    [KeyboardButton("🖼️ Скриншот экрана"), KeyboardButton("📋 Файлы на рабочем столе")],
    [KeyboardButton("🔊 Изменить громкость"), KeyboardButton("🌞 Изменить яркость")],
    [KeyboardButton("⭐ Быстрый доступ"), KeyboardButton("➡️ Дальше")],
    [KeyboardButton("🔒 Выйти"), KeyboardButton("❓ Помощь")],
]

EXTRA_COMMAND_BUTTONS = [
    [KeyboardButton("💻 Системная информация"), KeyboardButton("🗔 Управление окнами")],
    [KeyboardButton("⚙️ Диспетчер задач"), KeyboardButton("🖼️ Сменить обои")],
    [KeyboardButton("🎨 Сменить тему")],
    [KeyboardButton("📦 Установленные программы"), KeyboardButton("🌐 IP Адреса")],
    [KeyboardButton("📊 Графики нагрузки"), KeyboardButton("🗂️ Файловый менеджер")],
    [KeyboardButton("🌐 Открыть сайт"), KeyboardButton("📁 Открыть папку")],
    [KeyboardButton("💬 Сообщение на экран"), KeyboardButton("🔒 Заблокировать ПК")],
    [KeyboardButton("ℹ️ Инфо о ПК"), KeyboardButton("🖱️ Управление мышью")],

    [KeyboardButton("⬅️ Назад")],
]



# --- Инициализация бота ---
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# --- Управление состоянием пользователей ---
user_data = {}
auth_state = {}


def get_user_data_for(user_id: int) -> dict:
    """Return per-user data dict stored in global user_data mapping."""
    if user_id not in user_data:
        user_data[user_id] = {}
    return user_data[user_id]


def get_user_auth_state(user_id):
    if user_id not in auth_state:
        auth_state[user_id] = {
            "authenticated": False,
            "failed_attempts": 0,
            "lockout_until": 0,
        }
    return auth_state[user_id]


# --- Обработчики функций ---

async def show_file_browser(message: types.Message, path: str = None):
    keyboard = InlineKeyboardMarkup(row_width=2)
    user_id = message.from_user.id
    cleanup(user_id)
    if path is None:
        drives = get_available_drives()
        buttons = []
        for i, d in enumerate(drives):
            token = f"drv_{int(time.time())}_{i}"
            add_token(user_id, token, d)
            buttons.append(InlineKeyboardButton(f"💿 {d}", callback_data=f"fb_nav_{token}"))
        keyboard.add(*buttons)
        text = "🗂️ Файловый менеджер. Выберите диск:"
    else:
        contents = get_directory_contents(path)
        if contents is None:
            await message.answer("⛔️ Отказано в доступе или папка не найдена.")
            return

        text = f"<code>{path}</code>"
        buttons = []
        parent_dir = os.path.dirname(path)
        if parent_dir != path:
             token = f"up_{int(time.time())}"
             add_token(user_id, token, parent_dir)
             buttons.append(InlineKeyboardButton("⬆️ На уровень выше", callback_data=f"fb_up_{token}"))
        else:
            buttons.append(InlineKeyboardButton("⬆️ К списку дисков", callback_data="fb_nav_drives"))

        for i, d in enumerate(contents['dirs']):
            token = f"dir_{int(time.time())}_{i}"
            add_token(user_id, token, os.path.join(path, d))
            buttons.append(InlineKeyboardButton(f"📁 {d}", callback_data=f"fb_nav_{token}"))
        for f in contents['files']:
            buttons.append(InlineKeyboardButton(f"📄 {f}", callback_data="noop"))
        
        keyboard.add(*buttons)

    keyboard.add(InlineKeyboardButton("❌ Закрыть", callback_data="fb_close"))

    try:
        await bot.edit_message_text(text, message.chat.id, message.message_id, reply_markup=keyboard, parse_mode="HTML")
    except Exception:
        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


async def show_process_list(message: types.Message, page=0):
    processes = get_process_list()
    total_pages = math.ceil(len(processes) / PROCESS_LIST_PAGE_SIZE)
    start_index = page * PROCESS_LIST_PAGE_SIZE
    end_index = start_index + PROCESS_LIST_PAGE_SIZE
    processes_to_show = processes[start_index:end_index]

    keyboard = InlineKeyboardMarkup(row_width=1)
    for proc in processes_to_show:
        text = f"❌ {proc['name']} ({proc['pid']}) - {proc['memory_mb']:.2f} MB"
        keyboard.add(InlineKeyboardButton(text, callback_data=f"kill_{proc['pid']}"))

    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton("⬅️ Пред.", callback_data=f"tm_page_{page-1}")
        )
    nav_buttons.append(
        InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="noop")
    )
    if page < total_pages - 1:
        nav_buttons.append(
            InlineKeyboardButton("След. ➡️", callback_data=f"tm_page_{page+1}")
        )
    keyboard.row(*nav_buttons)
    keyboard.add(InlineKeyboardButton("🔄 Обновить", callback_data="tm_page_0"))
    # allow exiting to main menu at any time from process list
    keyboard.add(InlineKeyboardButton("🏠 Главное меню", callback_data="tm_home"))

    try:
        await bot.edit_message_text(
            "Диспетчер задач (отсортировано по памяти):",
            message.chat.id,
            message.message_id,
            reply_markup=keyboard,
        )
    except Exception:
        await message.answer(
            "Диспетчер задач (отсортировано по памяти):", reply_markup=keyboard
        )


async def show_installed_apps(message: types.Message, page=0):
    await message.answer("⏳ Собираю список программ, это может занять некоторое время...")
    apps = get_installed_apps()
    total_pages = math.ceil(len(apps) / APPS_PAGE_SIZE)
    start_index = page * APPS_PAGE_SIZE
    end_index = start_index + APPS_PAGE_SIZE
    apps_to_show = apps[start_index:end_index]

    response_text = "<b>Установленные программы:</b>\n\n"
    for i, app in enumerate(apps_to_show, start=start_index + 1):
        response_text += f"{i}. <code>{app['name']}</code> (Версия: {app['version']})\n"

    keyboard = InlineKeyboardMarkup()
    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton("⬅️ Пред.", callback_data=f"app_page_{page-1}")
        )
    nav_buttons.append(
        InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="noop")
    )
    if page < total_pages - 1:
        nav_buttons.append(
            InlineKeyboardButton("След. ➡️", callback_data=f"app_page_{page+1}")
        )
    keyboard.row(*nav_buttons)

    try:
        await bot.edit_message_text(
            response_text,
            message.chat.id,
            message.message_id,
            reply_markup=keyboard,
            parse_mode="HTML",
        )
    except Exception:
        await message.answer(response_text, reply_markup=keyboard, parse_mode="HTML")


async def handle_wallpaper_photo(message: types.Message):
    from commands.wallpaper_changer import FILES_BUTTONS
    await message.answer(
        "⏳ Скачиваю и устанавливаю обои...",
        reply_markup=types.ReplyKeyboardMarkup(keyboard=FILES_BUTTONS, resize_keyboard=True)
    )
    wallpaper_dir = os.path.join(os.path.dirname(__file__), "wallpapers")
    if not os.path.exists(wallpaper_dir):
        os.makedirs(wallpaper_dir)

    photo_id = message.photo[-1].file_id
    file = await bot.get_file(photo_id)
    destination_path = os.path.join(wallpaper_dir, f"{photo_id}.jpg")
    await bot.download_file(file.file_path, destination_path)

    success, result_message = set_wallpaper(destination_path)
    await message.answer(
        result_message,
        reply_markup=types.ReplyKeyboardMarkup(keyboard=FILES_BUTTONS, resize_keyboard=True)
    )
    # clear per-user awaiting flag
    ud = get_user_data_for(message.from_user.id)
    ud.pop("awaiting_wallpaper", None)


async def send_performance_graphs(message: types.Message):
    await message.answer("⏳ Создаю графики, это может занять несколько секунд...")
    graph_paths = generate_performance_graphs()
    if not graph_paths:
        await message.answer("Не удалось создать графики.")
        return

    for path in graph_paths:
        try:
            with open(path, "rb") as photo:
                await bot.send_photo(message.chat.id, photo)
        except Exception as e:
            await message.answer(f"Ошибка при отправке графика {os.path.basename(path)}: {e}")
        finally:
            if os.path.exists(path):
                os.remove(path)

    # after sending all graphs, show main menu keyboard so user can continue
    try:
        keyboard = ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True)
        await message.answer("Графики отправлены.", reply_markup=keyboard)
    except Exception:
        await message.answer("Графики отправлены.")


# --- Обработчики колбэков ---
@dp.callback_query_handler(lambda c: c.data.startswith("fb_"))
async def file_browser_callback(callback_query: types.CallbackQuery):
    # callback format: fb_<action>_<token>
    action_data = callback_query.data.split("_", 2)
    action = action_data[1]
    token = action_data[2] if len(action_data) > 2 else None
    user_id = callback_query.from_user.id

    # cleanup stale tokens and resolve token to path using per-user map (if applicable)
    cleanup(user_id)
    resolved = None
    if token:
        resolved = resolve_token(user_id, token)

    if action == "nav":
        if token == 'drives' or (token == 'drives'):
            await show_file_browser(callback_query.message, path=None)
        else:
            await show_file_browser(callback_query.message, path=resolved)
    elif action == "up":
        if resolved is None:
            await show_file_browser(callback_query.message, path=None)
        else:
            parent_path = os.path.dirname(resolved)
            if parent_path == resolved:
                await show_file_browser(callback_query.message, path=None)
            else:
                await show_file_browser(callback_query.message, path=parent_path)
    elif action == "close":
        # cleanup token map for this user
        clear_user(user_id)
        await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)

    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data.startswith("tm_page_"))
async def process_list_page_callback(callback_query: types.CallbackQuery):
    page = int(callback_query.data.split("_")[-1])
    await show_process_list(callback_query.message, page)
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data.startswith("kill_"))
async def kill_process_callback(callback_query: types.CallbackQuery):
    pid = int(callback_query.data.split("_")[-1])
    result = kill_process_by_pid(pid)
    await callback_query.answer(result, show_alert=True)
    await show_process_list(callback_query.message)


@dp.callback_query_handler(lambda c: c.data == "tm_home")
async def tm_home_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    # clear per-user state for this user and show main menu
    try:
        ud = get_user_data_for(user_id)
        ud.clear()
    except Exception:
        pass
    keyboard = ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True)
    try:
        # remove the inline message and send main menu keyboard
        await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    except Exception:
        pass
    await bot.send_message(callback_query.from_user.id, "Главное меню:", reply_markup=keyboard)
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data.startswith("set_theme_"))
async def set_theme_callback(callback_query: types.CallbackQuery):
    mode = callback_query.data.split("_")[-1]
    success, message = set_theme(mode)
    await callback_query.answer(message, show_alert=True)
    await bot.edit_message_text(
        f"{callback_query.message.text}\n\n{message}",
        callback_query.from_user.id,
        callback_query.message.message_id,
    )


# power modes removed


@dp.callback_query_handler(lambda c: c.data.startswith("app_page_"))
async def app_list_page_callback(callback_query: types.CallbackQuery):
    page = int(callback_query.data.split("_")[-1])
    await show_installed_apps(callback_query.message, page)
    await callback_query.answer()


# --- Основные обработчики сообщений ---
@dp.message_handler(commands=["start", "старт"])
async def start(message: types.Message):
    if message.from_user.id != AUTHORIZED_USER_ID:
        return await message.answer("⛔️ У вас нет доступа к этому боту.")
    state = get_user_auth_state(message.from_user.id)
    if state["authenticated"]:
        keyboard = ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True)
        await message.answer("✅ Вы уже в системе.", reply_markup=keyboard)
    else:
        await message.answer("🔒 Введите пароль:", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands=["logout", "выйти"])
async def logout(message: types.Message):
    state = get_user_auth_state(message.from_user.id)
    state["authenticated"] = False
    # clear only this user's data (don't wipe global mapping for all users)
    ud = get_user_data_for(message.from_user.id)
    ud.clear()
    await message.answer("🔒 Вы вышли из системы.", reply_markup=types.ReplyKeyboardRemove())


async def handle_commands(message: types.Message):
    # use per-user state dictionary
    user_id = message.from_user.id
    user_data = get_user_data_for(user_id)
    text = message.text

    # --- Быстрый доступ как отдельный stateful режим ---
    if user_data.get('quick_access_mode'):
        from commands.quick_access import handle_quick_access_choice
        result = await handle_quick_access_choice(message)
        if result == 'CANCELLED':
            # Сброс всех stateful-флагов, чтобы не было конфликтов после возврата
            for key in list(user_data.keys()):
                if key.endswith('_mode') or key.startswith('set_') or key in ('create_file','create_folder','open_program','open_folder','open_site','show_message','desktop_files_mode','window_action','youtube_mode'):
                    user_data.pop(key, None)
            await message.answer("Действие отменено.", reply_markup=ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True))
        return

    # --- Навигация и справка ---
    if text == "🏠 Главное меню":
        user_data.clear()
        keyboard = ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True)
        await message.answer("Главное меню:", reply_markup=keyboard)
        return
    elif text == "⬅️ Назад":
        user_data.clear()
        keyboard = ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True)
        await message.answer("Главное меню:", reply_markup=keyboard)
        return
    elif text == "➡️ Дальше":
        keyboard = ReplyKeyboardMarkup(keyboard=EXTRA_COMMAND_BUTTONS, resize_keyboard=True)
        await message.answer("Дополнительные команды:", reply_markup=keyboard)
        return
    elif text == "❓ Помощь":
        help_text = (
            "<b>ℹ️ Полная справка по функциям бота:</b>\n\n"
            "<b>Главное меню:</b>\n"
            "- ⏻ Выключить ПК — завершение работы компьютера (требует пароль).\n"
            "- 🔄 Перезагрузить ПК — перезапуск компьютера (требует пароль).\n"
            "- 📂 Создать папку — создать новую папку на рабочем столе.\n"
            "- 📄 Создать файл — создать новый файл на рабочем столе.\n"
            "- 🖥️ Открыть программу — запуск программ по имени.\n"
            "- ▶️ YouTube видео — управление YouTube-вкладками и открытие видео.\n"
            "- 🖼️ Скриншот экрана — сделать и получить скриншот.\n"
            "- 📋 Файлы на рабочем столе — список файлов с действиями.\n"
            "- 🔊 Изменить громкость — задать уровень громкости (0-100).\n"
            "- 🌞 Изменить яркость — задать уровень яркости (0-100).\n"
            "- ⭐ Быстрый доступ — открыть избранные папки.\n"
            "- ➡️ Дальше — дополнительные команды.\n"
            "- 🔒 Выйти — выйти из системы.\n"
            "- ❓ Помощь — эта справка.\n\n"
            "<b>Дополнительные команды:</b>\n"
            "- 💻 Системная информация — краткая информация о ПК.\n"
            "- 🗔 Управление окнами — управление окнами Windows.\n"
            "- ⚙️ Диспетчер задач — список процессов, завершение по PID.\n"
            "- 🖼️ Сменить обои — смена обоев рабочего стола.\n"
            "- 🎨 Сменить тему — светлая/тёмная тема Windows.\n"
            ""
            "- 📦 Установленные программы — список установленных приложений.\n"
            "- 🌐 IP Адреса — локальный и внешний IP.\n"
            "- 📊 Графики нагрузки — графики CPU/RAM/диска.\n"
            "- ️ Файловый менеджер — просмотр и управление файлами.\n"
            "- 🌐 Открыть сайт — открыть сайт в браузере.\n"
            "- 📁 Открыть папку — открыть папку по пути.\n"
            "- 💬 Сообщение на экран — показать сообщение на экране пользователя.\n"
            "- 🔒 Заблокировать ПК — заблокировать рабочую станцию.\n"
            "- ℹ️ Инфо о ПК — подробная информация о системе.\n"
            "- 🖱️ Управление мышью — эмуляция мыши.\n"
            "- 💻 Терминал — удалённый терминал (требует пароль).\n"
            "- ⬅️ Назад — вернуться в главное меню.\n\n"
            "<b>Навигация:</b>\n"
            "- '🏠 Главное меню' — возврат в главное меню из любого режима.\n"
            "- '⬅️ Назад' — шаг назад или отмена действия.\n"
            "- Для каждой команды доступны подсказки и кнопки для возврата.\n\n"
            "<b>Безопасность:</b>\n"
            "- Некоторые действия требуют повторного ввода пароля.\n"
            "- После 3 неверных попыток — временная блокировка.\n"
            "- Все команды доступны только авторизованному пользователю.\n"
        )
        await message.answer(help_text, parse_mode="HTML", reply_markup=ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True))
        return

    # --- Основные действия ---
    if text == "🔒 Заблокировать ПК":
        user_data['lock_pc'] = True
        await call_handler(lock_pc, message, user_data)
        return
    elif text == "🖼️ Скриншот экрана":
        await screenshot(message)
        return
    elif text == "ℹ️ Инфо о ПК":
        await system_info_full(message)
        return
    elif text == "🔒 Выйти":
        await logout(message)
        return
    if text == "📂 Создать папку":
        user_data['create_folder'] = True
        await call_handler(create_folder, message, user_data)
        return
    elif text == "📄 Создать файл":
        user_data['create_file'] = True
        await call_handler(create_file, message, user_data)
        return
    elif text == "🖥️ Открыть программу":
        user_data['open_program'] = True
        await call_handler(open_program, message, user_data)
        return
    elif text == "📋 Файлы на рабочем столе":
        await call_handler(files_on_desktop, message, user_data)
        try:
            await message.answer(f"[DBG_AFTER files_on_desktop] keys: {list(user_data.keys())}")
        except Exception:
            pass
        return
    elif text == "🔊 Изменить громкость":
        user_data['set_volume'] = True
        await call_handler(set_volume, message, user_data)
        return
    elif text == "🌞 Изменить яркость":
        user_data['set_brightness'] = True
        await call_handler(set_brightness, message, user_data)
        return
    elif text == "💬 Сообщение на экран":
        user_data['show_message'] = True
        await call_handler(show_message, message, user_data)
        return
    elif text == "🌐 Открыть сайт":
        user_data['open_site'] = True
        await call_handler(open_site, message, user_data)
        return
    elif text == "📁 Открыть папку":
        user_data['open_folder'] = True
        await call_handler(open_folder, message, user_data)
        return
    elif text == "🖼️ Сменить обои":
        user_data["awaiting_wallpaper"] = True
        from commands.wallpaper_changer import wallpaper_request_message
        await call_handler(wallpaper_request_message, message, user_data)
        return
    elif text == "⭐ Быстрый доступ":
        user_data['quick_access_mode'] = True
        await call_handler(quick_access_initial, message, user_data)
        return
    elif text == "▶️ YouTube видео":
        await call_handler(youtube, message, user_data)
        return
    elif text == "🎨 Сменить тему":
        keyboard = InlineKeyboardMarkup().row(
            InlineKeyboardButton("💡 Светлая", callback_data="set_theme_light"),
            InlineKeyboardButton("🌙 Темная", callback_data="set_theme_dark")
        )
        await message.answer("Выберите тему оформления:", reply_markup=keyboard)
        return
    elif text == "📦 Установленные программы":
        await call_handler(show_installed_apps, message, user_data)
        return
    elif text == "🌐 IP Адреса":
        await message.answer("⏳ Получаю IP адреса...")
        private_ip = get_private_ip()
        public_ip = get_public_ip()
        response_text = (
            f"<b>IP Адреса:</b>\n\n"
            f"🏠 <b>Локальный (внутренний):</b>\n<code>{private_ip}</code>\n\n"
            f"🌍 <b>Публичный (внешний):</b>\n<code>{public_ip}</code>"
        )
        await message.answer(response_text, parse_mode="HTML")
        return
    elif text == "💻 Системная информация":
        await system_info(message)
        return
    elif text == "🗔 Управление окнами":
        user_data['window_action'] = True
        await call_handler(window_manage, message, user_data)
        return
    elif text == "🖱️ Управление мышью":
        user_data['mouse_control_mode'] = True
        await call_handler(mouse_control, message, user_data)
        return


    # --- Команды, требующие пароля ---
    if text == "⏻ Выключить ПК":
        user_data["awaiting_password_for"] = "shutdown"
        await message.answer("🔒 Для подтверждения, введите пароль:", reply_markup=types.ReplyKeyboardRemove())
        return
    elif text == "🔄 Перезагрузить ПК":
        user_data["awaiting_password_for"] = "reboot"
        await message.answer("🔒 Для подтверждения, введите пароль:", reply_markup=types.ReplyKeyboardRemove())
        return
    elif text == "⚙️ Диспетчер задач":
        user_data["awaiting_password_for"] = "task_manager"
        await message.answer("🔒 Для доступа к диспетчеру задач, введите пароль:", reply_markup=types.ReplyKeyboardRemove())
        return
    # 'Режимы питания' удалены
    elif text == "📊 Графики нагрузки":
        user_data["awaiting_password_for"] = "performance_graphs"
        await message.answer("🔒 Для получения графиков производительности, введите пароль:", reply_markup=types.ReplyKeyboardRemove())
        return
    elif text == "🗂️ Файловый менеджер":
        user_data["awaiting_password_for"] = "file_browser"
        await message.answer("🔒 Для доступа к файловому менеджеру, введите пароль:", reply_markup=types.ReplyKeyboardRemove())
        return



    # --- Проверка пароля для опасных команд ---
    if user_data.get("awaiting_password_for"):
        command = user_data.pop("awaiting_password_for")
        password_attempt = message.text.encode("utf-8")
        await message.delete()
        # Проверяем пароль по всем хэшам
        for hash_bytes in BOT_PASSWORD_HASHES:
            try:
                if bcrypt.checkpw(password_attempt, hash_bytes):
                    await message.answer(f"✅ Пароль верный. Выполняю: {command}")
                    if command == "shutdown": await shutdown(message)
                    elif command == "reboot": await reboot(message)

                    elif command == "task_manager": await show_process_list(message)
                    elif command == "power_modes":
                        keyboard = InlineKeyboardMarkup().row(
                            InlineKeyboardButton(" Сон", callback_data="power_sleep"),
                            InlineKeyboardButton(" hib Гибернация", callback_data="power_hibernate"),
                        )
                        await message.answer("Выберите режим питания:", reply_markup=keyboard)
                    elif command == "performance_graphs": await send_performance_graphs(message)
                    elif command == "file_browser": await show_file_browser(message)
                    break
            except Exception as e:
                print(f"[DEBUG] Ошибка bcrypt.checkpw: {e}")
        else:
            await message.answer("⛔️ Неверный пароль. Команда отменена.")
        return

    # --- Stateful режимы (многошаговые) ---
    stateful_commands = {
        'create_folder': create_folder_name,
        'create_file': create_file_name,
        'set_volume': set_volume_value,
        'set_brightness': set_brightness_value,
        'show_message': show_message_text,
        'open_site': open_site_link,
        'open_folder': open_folder_path,
        'open_program': open_program_name,
        'mouse_control_mode': mouse_action,
        'window_action': window_action,
        'desktop_files_mode': files_on_desktop_action,
        'youtube_mode': youtube_link
    }

    for state, handler in stateful_commands.items():
        if user_data.get(state):
            result = await call_handler(handler, message, user_data)
            if result == 'CANCELLED':
                user_data.pop(state, None)
                await message.answer("Действие отменено.", reply_markup=ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True))
            return

    # Если ничего не подошло
    # Debug: если пользователь ввёл цифру, покажем текущее per-user состояние (временно)
    try:
        if text and text.strip().isdigit():
            await message.answer(f"[DEBUG] user_data keys: {list(user_data.keys())}\ndesktop_files_mode={user_data.get('desktop_files_mode')}\ndesktop_files_list_len={len(user_data.get('desktop_files_list', []))}")
    except Exception:
        pass
    await message.answer("Неизвестная команда.")


async def handle_password_attempt(message: types.Message):
    user_id = message.from_user.id
    state = get_user_auth_state(user_id)

    if time.time() < state["lockout_until"]:
        await message.delete()
        await message.answer(
            f"🔒 Попробуйте снова через {int((state['lockout_until'] - time.time()) / 60)} минут."
        )
        return

    password_attempt = message.text.encode("utf-8")
    await message.delete()

    # Проверяем пароль по всем хэшам
    for hash_bytes in BOT_PASSWORD_HASHES:
        print(f"[DEBUG] Проверка пароля: {password_attempt} против хэша: {hash_bytes}")
        try:
            result = bcrypt.checkpw(password_attempt, hash_bytes)
            print(f"[DEBUG] Результат bcrypt.checkpw: {result}")
        except Exception as e:
            print(f"[DEBUG] Ошибка bcrypt.checkpw: {e}")
            result = False
        if result:
            state["authenticated"] = True
            state["failed_attempts"] = 0
            keyboard = ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True)
            await message.answer("✅ Пароль верный.", reply_markup=keyboard)
            break
    else:
        state["failed_attempts"] += 1
        if state["failed_attempts"] >= MAX_LOGIN_ATTEMPTS:
            state["lockout_until"] = time.time() + LOCKOUT_DURATION
            await message.answer(
                f"⛔️ Доступ заблокирован на {int(LOCKOUT_DURATION / 60)} минут."
            )
        else:
            await message.answer("⛔️ Неверный пароль.")


@dp.message_handler(content_types=[types.ContentType.TEXT, types.ContentType.PHOTO])
async def main_message_handler(message: types.Message):
    if message.from_user.id != AUTHORIZED_USER_ID:
        return await message.answer("⛔️ У вас нет доступа к этому боту.")
    state = get_user_auth_state(message.from_user.id)
    if state["authenticated"]:
        # per-user data for this chat
        ud = get_user_data_for(message.from_user.id)
        if message.content_type == "photo":
            if ud.get("awaiting_wallpaper"):
                await handle_wallpaper_photo(message)
            else:
                await message.answer(
                    "🖼️ Я не ожидал фото. Если хотите сменить обои, используйте команду."
                )
        else:
            await handle_commands(message)
    else:
        if message.content_type == "text":
            await handle_password_attempt(message)
        else:
            await message.answer("🔒 Сначала войдите в систему.")


# --- Запуск бота ---
async def on_startup(dp):
    if not all([TOKEN, AUTHORIZED_USER_ID, BOT_PASSWORD_HASHES]):
        print("CRITICAL ERROR: Missing environment variables")
        return
    try:
        await bot.send_message(
            chat_id=AUTHORIZED_USER_ID, text="<b>✅ Бот запущен! Введите пароль для входа.</b>", parse_mode="HTML"
        )
    except Exception as e:
        print(f"Ошибка отправки сообщения о запуске: {e}")


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)