import os
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Пути к папкам
FOLDER_PATHS = {
    "Документы": r"D:\\быстрый доступ\\документы",
    "Загрузки": r"D:\\быстрый доступ\\загрузки",
    "Музыка": r"D:\\быстрый доступ\\музыка",
    "Рабочий стол": r"C:\\Users\\xylixqe\\Desktop",
    "Картинки": r"D:\\быстрый доступ\\изображения",
    "Видео": r"D:\\быстрый доступ\\видео",
}

# Клавиатура для этого режима
QUICK_ACCESS_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(name) for name in list(FOLDER_PATHS.keys())[i:i+3]] for i in range(0, len(FOLDER_PATHS), 3)
    ] + [
        [KeyboardButton("🏠 Главное меню"), KeyboardButton("⬅️ Назад")]
    ],
    resize_keyboard=True
)

async def quick_access_initial(message, user_data: dict = None):
    """Отправляет первоначальное сообщение с кнопками."""
    await message.answer(
        "Выберите папку для быстрого доступа:",
        reply_markup=QUICK_ACCESS_KEYBOARD
    )

async def handle_quick_access_choice(message, user_data: dict = None):
    """Обрабатывает выбор пользователя и возвращает сигнал об отмене при необходимости."""
    if message.text in ["🏠 Главное меню", "⬅️ Назад", "/cancel"]:
        return "CANCELLED"

    path = FOLDER_PATHS.get(message.text)
    if path and os.path.exists(path):
        try:
            os.startfile(path)
            await message.answer(f"✅ Открываю папку: {message.text}", reply_markup=QUICK_ACCESS_KEYBOARD)
        except Exception as e:
            await message.answer(f"⛔ Ошибка открытия папки: {e}", reply_markup=QUICK_ACCESS_KEYBOARD)
    else:
        await message.answer("Неизвестная папка или путь не найден.", reply_markup=QUICK_ACCESS_KEYBOARD)
    
    return None
