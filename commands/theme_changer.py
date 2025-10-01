import winreg

KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"

def set_theme(mode: str) -> tuple[bool, str]:
    """
    Устанавливает светлую или темную тему для приложений и системы в Windows.

    Args:
        mode: 'light' или 'dark'.

    Returns:
        Кортеж (успех, сообщение).
    """
    if mode not in ['light', 'dark']:
        return False, "Недопустимый режим. Используйте 'light' или 'dark'."

    value = 1 if mode == 'light' else 0
    theme_name = "Светлая" if mode == 'light' else "Темная"

    try:
        # Открываем ключ реестра с правами на запись
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, KEY_PATH, 0, winreg.KEY_SET_VALUE)

        # Устанавливаем значения для темы приложений и системы
        winreg.SetValueEx(key, "AppsUseLightTheme", 0, winreg.REG_DWORD, value)
        winreg.SetValueEx(key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, value)

        # Закрываем ключ
        winreg.CloseKey(key)

        return True, f"Тема успешно изменена на '{theme_name}'."

    except FileNotFoundError:
        return False, "Не удалось найти ключ реестра. Возможно, ваша версия Windows не поддерживается."
    except Exception as e:
        return False, f"Произошла ошибка при изменении реестра: {e}"

from aiogram.types import ReplyKeyboardMarkup


async def theme_changer_handler(message, user_data: dict = None):
    """Simple handler to set theme with cancel/back support. Expects text 'light' or 'dark'."""
    if user_data is None:
        user_data = {}
    if message.text in ["🏠 Главное меню", "⬅️ Назад", "/cancel"]:
        try:
            from bot import MAIN_COMMAND_BUTTONS
            await message.answer("Возврат в главное меню.", reply_markup=ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True))
        except Exception:
            await message.answer("Возврат в главное меню.")
        return 'CANCELLED'

    mode = message.text.strip().lower()
    ok, msg = set_theme(mode)
    await message.answer(msg)
