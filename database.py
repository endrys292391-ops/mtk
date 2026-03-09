import sqlite3
from datetime import datetime
from config import DATABASE_PATH

def get_db():
    """Получить соединение с БД"""
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Создать таблицы если их нет"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Пользователи
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            role TEXT DEFAULT 'user',
            subscribed INTEGER DEFAULT 0,
            created_at TIMESTAMP
        )
    ''')
    
    # Подписки
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            class_name TEXT,
            expires_at TIMESTAMP,
            created_at TIMESTAMP
        )
    ''')
    
    # Расписание (кеш)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedule_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_name TEXT,
            day TEXT,
            data TEXT,
            updated_at TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ База данных инициализирована")

# Создаем таблицы при запуске
init_db()