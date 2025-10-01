import socket
import requests
from aiogram.types import ReplyKeyboardMarkup

def get_private_ip() -> str:
    """Получает локальный IP-адрес компьютера."""
    try:
        # Создаем сокет для получения локального IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        # Подключаемся к любому внешнему адресу (не отправляя данные)
        s.connect(('8.8.8.8', 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        # Резервный метод, если первый не сработал
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception as e:
            return f"Не удалось получить локальный IP: {e}"

def get_public_ip() -> str:
    """Получает публичный IP-адрес с помощью внешнего сервиса."""
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        response.raise_for_status()  # Проверка на HTTP ошибки
        return response.json()['ip']
    except requests.exceptions.RequestException as e:
        return f"Не удалось получить публичный IP: {e}"
    except Exception as e:
        return f"Произошла непредвиденная ошибка: {e}"


async def ip_info_handler(message, user_data=None):
    if user_data is None:
        user_data = {}
    if message.text in ["🏠 Главное меню", "⬅️ Назад", "/cancel"]:
        try:
            from bot import MAIN_COMMAND_BUTTONS
            await message.answer("Возврат в главное меню.", reply_markup=ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True))
        except Exception:
            await message.answer("Возврат в главное меню.")
        return 'CANCELLED'

    private = get_private_ip()
    public = get_public_ip()
    await message.answer(f"Локальный IP: {private}\nПубличный IP: {public}")
