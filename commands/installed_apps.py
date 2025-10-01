import winreg

def get_installed_apps() -> list[dict]:
    """
    Сканирует реестр Windows для получения списка установленных программ.
    Возвращает отсортированный список словарей с ключами 'name' и 'version'.
    """
    app_list = []
    uninstall_paths = [
        r"Software\Microsoft\Windows\CurrentVersion\Uninstall",
        r"Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]
    
    hives = [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]

    for hive in hives:
        for path in uninstall_paths:
            try:
                with winreg.OpenKey(hive, path) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        sub_key_name = winreg.EnumKey(key, i)
                        try:
                            with winreg.OpenKey(key, sub_key_name) as sub_key:
                                name = winreg.QueryValueEx(sub_key, "DisplayName")[0]
                                try:
                                    version = winreg.QueryValueEx(sub_key, "DisplayVersion")[0]
                                except FileNotFoundError:
                                    version = "N/A"
                                
                                # Фильтруем системные компоненты и обновления
                                if name and not name.startswith("KB") and "update" not in name.lower():
                                    app_list.append({"name": name, "version": version})
                        except (FileNotFoundError, OSError):
                            continue
            except FileNotFoundError:
                continue

    # Удаляем дубликаты и сортируем
    unique_apps = [dict(t) for t in {tuple(d.items()) for d in app_list}]
    sorted_apps = sorted(unique_apps, key=lambda x: x['name'].lower())
    
    return sorted_apps


from aiogram.types import ReplyKeyboardMarkup


async def installed_apps_handler(message, user_data: dict = None):
    if user_data is None:
        user_data = {}
    # allow cancel/back
    if message.text in ["🏠 Главное меню", "⬅️ Назад", "/cancel"]:
        try:
            from bot import MAIN_COMMAND_BUTTONS
            await message.answer("Возврат в главное меню.", reply_markup=ReplyKeyboardMarkup(keyboard=MAIN_COMMAND_BUTTONS, resize_keyboard=True))
        except Exception:
            await message.answer("Возврат в главное меню.")
        return 'CANCELLED'

    apps = get_installed_apps()
    msg = "Список установленных приложений:\n" + "\n".join(f"{a['name']} - {a['version']}" for a in apps[:200])
    await message.answer(msg)
