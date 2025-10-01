import screen_brightness_control as sbc
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Клавиатура для режима установки яркости
SET_BRIGHTNESS_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("🏠 Главное меню"), KeyboardButton("⬅️ Назад")]
    ],
    resize_keyboard=True
)

async def set_brightness(message, user_data: dict = None):
    await message.answer(
        "Введите уровень яркости от 0 до 100:",
        reply_markup=SET_BRIGHTNESS_KEYBOARD
    )

async def set_brightness_value(message, user_data: dict = None):
    if message.text in ["🏠 Главное меню", "⬅️ Назад", "/cancel"]:
        return "CANCELLED"

    try:
        brightness = int(message.text.strip())
        if not (0 <= brightness <= 100):
            raise ValueError("Яркость должна быть в диапазоне от 0 до 100.")

        sbc.set_brightness(brightness)
        await message.answer(f"✅ Яркость установлена на {brightness}%.\n\nВведите новое значение или вернитесь в меню.", reply_markup=SET_BRIGHTNESS_KEYBOARD)

    except ValueError as e:
        await message.answer(f"⛔ Ошибка: {e}. Пожалуйста, введите число от 0 до 100.", reply_markup=SET_BRIGHTNESS_KEYBOARD)
    except Exception as e:
        await message.answer(f"⛔ Произошла системная ошибка: {e}", reply_markup=SET_BRIGHTNESS_KEYBOARD)
        return "CANCELLED"
    return None