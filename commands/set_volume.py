from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Клавиатура для режима установки громкости
SET_VOLUME_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("🏠 Главное меню"), KeyboardButton("⬅️ Назад")]
    ],
    resize_keyboard=True
)

async def set_volume(message, user_data: dict = None):
    await message.answer(
        "Введите уровень громкости от 0 до 100:",
        reply_markup=SET_VOLUME_KEYBOARD
    )

async def set_volume_value(message, user_data: dict = None):
    if message.text in ["🏠 Главное меню", "⬅️ Назад", "/cancel"]:
        return "CANCELLED"

    try:
        volume = int(message.text.strip())
        if not (0 <= volume <= 100):
            raise ValueError("Громкость должна быть в диапазоне от 0 до 100.")

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume_interface = interface.QueryInterface(IAudioEndpointVolume)
        volume_interface.SetMasterVolumeLevelScalar(volume / 100, None)
        await message.answer(f"✅ Громкость установлена на {volume}%.\n\nВведите новое значение или вернитесь в меню.", reply_markup=SET_VOLUME_KEYBOARD)
    except ValueError as e:
        await message.answer(f"⛔ Ошибка: {e}. Пожалуйста, введите число от 0 до 100.", reply_markup=SET_VOLUME_KEYBOARD)
    except Exception as e:
        await message.answer(f"⛔ Произошла системная ошибка: {e}", reply_markup=SET_VOLUME_KEYBOARD)
        return "CANCELLED"
    return None