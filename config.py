import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Токен бота
BOT_TOKEN = "7618653140:AAFLWh4VFiKb3Ig6c0tQNyEi0byxdhC0Usk"

# ТВОЙ ID (админ)
ADMIN_ID = 8591272970

# База данных
DATABASE_PATH = BASE_DIR / "bot_database.db"

# Лог файл
LOG_FILE = BASE_DIR / "bot.log"

# Настройки парсинга
USE_SELENIUM = False
