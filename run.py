#!/usr/bin/env python
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from config import BOT_TOKEN
import handlers

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='bot.log'
)
logger = logging.getLogger(__name__)

def main():
    """Запуск бота"""
    print("🚀 Запуск бота...")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем все хендлеры
    handlers.register_handlers(app)
    
    print("✅ Бот успешно запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()