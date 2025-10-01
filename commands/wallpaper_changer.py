import ctypes
import os
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram import types

FILES_BUTTONS = [
    [KeyboardButton("🏠 Главное меню")],
    [KeyboardButton("⬅️ Назад")],
]


def set_wallpaper(image_path: str) -> tuple[bool, str]:
    SPI_SETDESKWALLPAPER = 20
    # SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    SPIF_FLAGS = 1 | 2

    try:
        # Убедимся, что путь является абсолютным
        abs_path = os.path.abspath(image_path)
        
        if not os.path.exists(abs_path):
            return False, f"Ошибка: Файл не найден по пути {abs_path}"

        # Определяем папку с обоями
        wallpaper_dir = os.path.dirname(abs_path)
        current_wallpaper_path = os.path.join(os.path.dirname(__file__), "..", "wallpapers", "current_wallpaper.txt")

        # Вызываем функцию Windows API
        if ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, abs_path, SPIF_FLAGS):
            # Если есть предыдущие обои, удаляем их
            try:
                if os.path.exists(current_wallpaper_path):
                    with open(current_wallpaper_path, 'r') as f:
                        old_wallpaper = f.read().strip()
                        if os.path.exists(old_wallpaper) and old_wallpaper != abs_path:
                            os.remove(old_wallpaper)
            except Exception:
                pass  # Игнорируем ошибки при удалении старых обоев

            # Сохраняем путь к новым обоям
            try:
                os.makedirs(os.path.dirname(current_wallpaper_path), exist_ok=True)
                with open(current_wallpaper_path, 'w') as f:
                    f.write(abs_path)
            except Exception:
                pass  # Игнорируем ошибки при сохранении пути

            return True, "Обои рабочего стола успешно изменены."
        else:
            return False, "Не удалось изменить обои через системный вызов."
        
    except Exception as e:
        return False, f"Произошла непредвиденная ошибка: {e}"

async def change_wallpaper(message: types.Message, user_data: dict = None):
    if user_data is None:
        user_data = {}
    # Всегда показываем кнопки FILES_BUTTONS при любом запросе
    if message.text in ["🏠 Главное меню", "⬅️ Назад", "/cancel"]:
        user_data.clear()
        await message.answer("Отмена изменения обоев.", reply_markup=ReplyKeyboardMarkup(keyboard=FILES_BUTTONS, resize_keyboard=True))
        return 'CANCELLED'


    if message.content_type == "text":
        image_path = message.text.strip()
        if not os.path.exists(image_path):
            await message.answer(f"Файл не найден: {image_path}", reply_markup=FILES_BUTTONS)
            return
        ok, msg = set_wallpaper(image_path)
        await message.answer(msg, reply_markup=FILES_BUTTONS)
        return
    elif message.content_type == "photo":
        try:
            # Создаем папку wallpapers, если её нет
            wallpaper_dir = os.path.join(os.path.dirname(__file__), "..", "wallpapers")
            os.makedirs(wallpaper_dir, exist_ok=True)
            
            # Генерируем уникальное имя файла
            photo_path = os.path.join(wallpaper_dir, f"wallpaper_{message.message_id}.jpg")
            
            # Скачиваем фото
            await message.photo[-1].download(destination_file=photo_path)
            
            # Устанавливаем обои
            ok, msg = set_wallpaper(photo_path)
            await message.answer(msg, reply_markup=FILES_BUTTONS)
        except Exception as e:
            await message.answer(f"Ошибка при установке обоев: {str(e)}", reply_markup=FILES_BUTTONS)
        return
    else:
        await message.answer("Ожидается путь к файлу или фото.", reply_markup=FILES_BUTTONS)
        return

async def wallpaper_request_message(message: types.Message, user_data: dict = None):
    if user_data is None:
        user_data = {}
    await message.answer(
        "🖼️ Пришлите изображение, которое хотите установить на рабочий стол:",
        reply_markup=ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton("🏠 Главное меню")],
            [KeyboardButton("⬅️ Назад")],
        ], resize_keyboard=True)
    )



# Переместите функцию async вне set_wallpaper
from aiogram.types import ReplyKeyboardMarkup




