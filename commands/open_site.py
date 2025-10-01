import os
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Клавиатура для режима открытия сайта
OPEN_SITE_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("🏠 Главное меню"), KeyboardButton("⬅️ Назад")]
    ],
    resize_keyboard=True
)

async def open_site(message, user_data: dict = None):
    await message.answer(
        "Введите полную ссылку на сайт (например, https://google.com):",
        reply_markup=OPEN_SITE_KEYBOARD
    )

async def open_site_link(message, user_data: dict = None):
    if user_data is None:
        user_data = {}
    if message.text in ["🏠 Главное меню", "⬅️ Назад", "/cancel"]:
        return "CANCELLED"

    url = message.text.strip()
    if url.startswith("http://") or url.startswith("https://"):
        try:
            os.system(f'start "" "{url}"')
            await message.answer(f"✅ Сайт {url} открыт в браузере.\n\nМожете ввести ещё одну ссылку или вернуться в меню.", reply_markup=OPEN_SITE_KEYBOARD)
        except Exception as e:
            await message.answer(f"⛔ Ошибка открытия сайта: {e}", reply_markup=OPEN_SITE_KEYBOARD)
            return "CANCELLED"
    else:
        await message.answer("⛔ Некорректная ссылка. Она должна начинаться с http:// или https://", reply_markup=OPEN_SITE_KEYBOARD)
    return None