import psutil
from aiogram.types import ReplyKeyboardMarkup

async def task_manager_handler(message, user_data=None):
    """Handler for task manager interactions with cancel/back support.
    Commands supported in message.text:
      - list
      - kill <pid>
    """
    if message.text in ["🏠 Главное меню", "⬅️ Назад", "/cancel"]:
        try:
            from bot import MAIN_COMMAND_BUTTONS
            await message.answer("Возврат в главное меню.", reply_markup=ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True))
        except Exception:
            await message.answer("Возврат в главное меню.")
        return 'CANCELLED'

    text = message.text.strip()
    if text.lower() == 'list':
        procs = get_process_list()
        msg = '\n'.join(f"{p['pid']} {p['name']} {p['memory_mb']:.1f}MB" for p in procs[:30])
        try:
            from bot import MAIN_COMMAND_BUTTONS
            await message.answer(msg or 'No processes found', reply_markup=ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True))
        except Exception:
            await message.answer(msg or 'No processes found')
        return

    if text.lower().startswith('kill'):
        parts = text.split()
        if len(parts) < 2 or not parts[1].isdigit():
            try:
                from bot import MAIN_COMMAND_BUTTONS
                await message.answer('Usage: kill <pid>', reply_markup=ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True))
            except Exception:
                await message.answer('Usage: kill <pid>')
            return
        pid = int(parts[1])
        res = kill_process_by_pid(pid)
        try:
            from bot import MAIN_COMMAND_BUTTONS
            await message.answer(res, reply_markup=ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True))
        except Exception:
            await message.answer(res)
        return

    try:
        from bot import MAIN_COMMAND_BUTTONS
        await message.answer("Команда не распознана. Используйте 'list' или 'kill <pid>'.", reply_markup=ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True))
    except Exception:
        await message.answer("Команда не распознана. Используйте 'list' или 'kill <pid>'.")

def get_process_list():
    """Возвращает отсортированный список процессов."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            # Получаем информацию о процессе
            pinfo = proc.info
            # Считаем использование памяти в МБ
            pinfo['memory_mb'] = pinfo['memory_info'].rss / (1024 * 1024)
            processes.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    # Сортируем процессы по использованию памяти (от большего к меньшему)
    sorted_processes = sorted(processes, key=lambda p: p['memory_mb'], reverse=True)
    return sorted_processes

def kill_process_by_pid(pid):
    """Завершает процесс по его PID."""
    try:
        p = psutil.Process(pid)
        p.kill()
        return f"Процесс {pid} успешно завершен."
    except psutil.NoSuchProcess:
        return f"Ошибка: Процесс с PID {pid} не найден."
    except psutil.AccessDenied:
        return f"Ошибка: Отказано в доступе для завершения процесса {pid}. Требуются права администратора."
    except Exception as e:
        return f"Произошла непредвиденная ошибка: {e}"
