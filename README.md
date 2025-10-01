# 🖥️ PC Admin Bot

### About the Bot

**PC Admin Bot** is a powerful and multifunctional Telegram bot designed for complete remote management of your Windows computer. With it, you can perform a wide range of tasks: from simple operations like shutdown or restart to advanced system administration, including process management, system settings modification, and executing terminal commands.

The bot is designed with a focus on security, using two-factor authentication (user ID + password) and protection for critical commands.

### ✨ Features

- **Power Management:** Shutdown, restart.
- **System Monitoring:**
    - Interactive Task Manager (view and terminate processes).
    - List of installed programs with pagination.
    - Performance graphs (CPU, RAM, Disk) as images.
- **Windows Customization:**
    - Change desktop wallpaper (send an image).
    - Switch between light and dark themes.
- **File and Program Management:**
    - Create folders and files.
    - Launch programs.
- **Interactive Commands:**
    - Terminal for executing Windows commands.
    - Mouse control, opening websites/folders, displaying on-screen messages.

---

## 🇬🇧 Full English Guide

### Summary
This repository contains PC Admin Bot — a Telegram bot for remote management of Windows PCs.

### Setting Up the Environment (Manual)
The repository includes a `.env` file. Fill in the values manually:
- `TOKEN` — token from @BotFather
- `AUTHORIZED_USER_ID` — your numeric Telegram ID
- `WOL_MAC_ADDRESS` — optional, format AA:BB:CC:DD:EE:FF
- `BOT_PASSWORD_HASHES` — one or more bcrypt strings, separated by commas

Example content:
```
TOKEN=1234567890:ABCDefGhIJKlmNoPqR
AUTHORIZED_USER_ID=123456789
BOT_PASSWORD_HASHES=$2b$12$...
WOL_MAC_ADDRESS=AA:BB:CC:DD:EE:FF
```

For generating bcrypt hashes, use `generate_hash.py` or `set_password.bat` (if Python is installed). More details in the "Password Setup" section.

If you don't know where to get the token or ID — check the "Where to Get Token/ID" section below.

### Where to Get Token and ID
- Bot token: use the official bot `@BotFather` in Telegram. The command `/newbot` creates a bot and provides a token.
- Your Telegram User ID: use the bot `@userinfobot` or `@get_id_bot`.

### Installing Python 3.11.9 (Windows)
1. Download the Python 3.11.9 installer (Windows) from the official site:
    - https://www.python.org/downloads/release/python-3119/
2. During installation, check "Add Python to PATH".
3. After installation, run in PowerShell:

```powershell
python --version
pip --version
```

Should print Python 3.11.9 version.

### Installing Dependencies
Open PowerShell in the project folder and run:

```powershell
pip install -r requirements.txt
```

### Building EXE with PyInstaller

#### Automatic Build
After setting up all necessary components (installing Python, dependencies, PyInstaller, configuring .env file and passwords), 
you can use the automatic build:

1. Just run the `build.bat` file in the project's root folder
2. The script will automatically build the bot and place the output file in the `dist` folder
3. Copy the `.env` file to the `dist` folder next to `bot.exe`

#### Manual Build
If you want to build the bot manually:
1. Install PyInstaller:
```
pip install pyinstaller
```
2. Build exe:
```
pyinstaller --onefile --noconsole --icon=icon.ico --add-data "wallpapers;wallpapers" bot.py
```
- Note: do not include the `commands` folder via `--add-data` — it's unnecessary, Python modules are automatically included in the build.
- The `.env` file MUST NOT be included in the built exe (it contains secrets). After building, place the local `.env` next to the `dist\bot.exe` executable
- The `--icon` parameter is optional — specify the path to your .ico file
- The result will be in the `dist` folder

### Autostart and Background Operation
    
#### Adding to Windows Startup
1. Press Win + R and type `shell:startup`
2. Copy the bot's shortcut (bot.exe) from the dist folder to the opened startup folder
3. The bot will now automatically start when Windows starts
    
#### Background Operation
- The bot runs completely in the background without displaying a console window
- You can check its operation in the task manager (process bot.exe)
- To stop the bot, use the task manager or the exit command in the bot itself
    
### Modifying and Adding Commands
If you want to add your own commands or modify existing ones:
1. Delete the old compiled bot.exe file from the dist folder
2. Make the necessary changes to the code
3. Rebuild the bot using build.bat or manual build
4. Replace the old file in the startup folder (if used)

### Password Setup
Two tools are available for creating password hashes:

- Directly running the Python script (recommended, supports multiple passwords separated by commas):

```powershell
python generate_hash.py
# or pass passwords as an argument (comma-separated):
python generate_hash.py --password "pass1,pass2"
```

The script will output a single line in the format:

```text
BOT_PASSWORD_HASHES=$2b$...,$2b$...  # hashes, separated by commas
```

- The `set_password.bat` utility runs `generate_hash.py` in the current console (password input will be visible). After the script completes, copy and paste the resulting string into `.env`. Example run:

```powershell
cd "C:\path\to\project"
.\set_password.bat
```

Note: generating a bcrypt hash requires Python and the `bcrypt` package to be installed.

### Replacing the Icon
Create or download an .ico file and provide the path in the `--icon` key when calling PyInstaller (see above).

### Creating Custom Commands

#### Command Structure
Each command in the bot is a separate Python file in the `commands/` folder. 
Commands follow a simple structure:

```python
async def command_handler(message, user_data=None):
    """Main command handler"""
    if message.text in ["🏠 Main Menu", "⬅️ Back", "/cancel"]:
        # Handle cancel/back
        try:
            from bot import MAIN_COMMAND_BUTTONS
            await message.answer(
                "Returning to main menu.",
                reply_markup=__import__('aiogram').types.ReplyKeyboardMarkup(
                    keyboard=MAIN_COMMAND_BUTTONS, 
                    resize_keyboard=True
                ),
            )
        except Exception:
            await message.answer("Returning to main menu.")
        return

    # Your command logic here
    await message.answer("Command execution result")

def some_helper_function():
    """Helper function for the command"""
    pass
```

#### Step-by-Step Guide to Adding a Command

1. Create a new file in the `commands/` folder, e.g., `my_command.py`

    2. Import the necessary modules:
    ```python
    from aiogram import types
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    ```

    3. Create the main command handler:
    ```python
    async def my_command_handler(message, user_data=None):
        # Your code here
        pass
    ```

    4. Import in `bot.py`:
    ```python
    from commands.my_command import my_command_handler
    ```

    5. Add a button to the menu (in `bot.py`):
    ```python
    MAIN_COMMAND_BUTTONS = [
        # Existing buttons...
        [KeyboardButton("🆕 My Command")],
    ]
    ```

    6. Add handling in the main handler (in `bot.py`):
    ```python
    elif text == "🆕 My Command":
        await my_command_handler(message, user_data)
        return
    ```

    #### Example of a Simple Command
    Here is an example of a command that shows the current time:

    ```python
    # commands/show_time.py
    from datetime import datetime
    from aiogram import types
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

    async def show_time_handler(message, user_data=None):
        if message.text in ["🏠 Main Menu", "⬅️ Back", "/cancel"]:
            try:
                from bot import MAIN_COMMAND_BUTTONS
                await message.answer(
                    "Returning to main menu.",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=MAIN_COMMAND_BUTTONS, 
                        resize_keyboard=True
                    ),
                )
            except Exception:
                await message.answer("Returning to main menu.")
            return

        current_time = datetime.now().strftime("%H:%M:%S")
        await message.answer(f"🕒 Current time: {current_time}")

    ```

    #### Tips for Creating Commands
    - Always handle return to the main menu
    - Use `user_data` for storing state between messages
    - Add informative emojis to messages
    - Split complex logic into separate functions
    - Document the code and command features
    - Handle possible errors and provide clear messages
    - Maintain a consistent style with other commands

    ### If Something Goes Wrong
    Open `README.md` and check the sections above.

    ---


