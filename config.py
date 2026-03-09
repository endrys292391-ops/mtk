import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Токен бота (вставь свой)
BOT_TOKEN = "8241703921:AAEeGhfVfySLxE0rfI9PA6q9SeYdKsn2nxA"

# База данных
DATABASE_PATH = BASE_DIR / "bot_database.db"

# Логи
LOG_FILE = BASE_DIR / "bot.log"

# Настройки парсинга
USE_SELENIUM = False  # Отключаем Selenium если не нужен