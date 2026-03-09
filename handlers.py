import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from database import get_db
from config import ADMIN_ID

logger = logging.getLogger(__name__)

# ========== СТАРТ ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user = update.effective_user
    
    # Сохраняем пользователя
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name, created_at)
        VALUES (?, ?, ?, ?)
    ''', (user.id, user.username, user.first_name, datetime.now()))
    conn.commit()
    conn.close()
    
    text = (
        f"👋 **Привет, {user.first_name}!**\n\n"
        "Я бот с расписанием занятий.\n\n"
        "📚 **Доступные команды:**\n"
        "/schedule - посмотреть расписание\n"
        "/subscribe - подписаться на обновления\n"
        "/help - помощь\n"
    )
    
    if user.id == ADMIN_ID:
        text += "\n👑 У вас есть права администратора."
    
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# ========== РАСПИСАНИЕ ==========
async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать расписание"""
    keyboard = [
        [InlineKeyboardButton("📅 Понедельник", callback_data="schedule_mon")],
        [InlineKeyboardButton("📅 Вторник", callback_data="schedule_tue")],
        [InlineKeyboardButton("📅 Среда", callback_data="schedule_wed")],
        [InlineKeyboardButton("📅 Четверг", callback_data="schedule_thu")],
        [InlineKeyboardButton("📅 Пятница", callback_data="schedule_fri")],
        [InlineKeyboardButton("📅 Суббота", callback_data="schedule_sat")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📚 **Выбери день недели:**",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

async def schedule_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора дня"""
    query = update.callback_query
    await query.answer()
    
    day_map = {
        "schedule_mon": "Понедельник",
        "schedule_tue": "Вторник",
        "schedule_wed": "Среда",
        "schedule_thu": "Четверг",
        "schedule_fri": "Пятница",
        "schedule_sat": "Суббота"
    }
    
    day = day_map.get(query.data, "Неизвестно")
    
    # Здесь должен быть твой код получения расписания
    text = f"📅 **{day}**\n\n"
    text += "8:30 - 9:15: Математика\n"
    text += "9:25 - 10:10: Русский язык\n"
    text += "10:20 - 11:05: Физика\n"
    text += "11:25 - 12:10: История\n"
    text += "12:20 - 13:05: Физкультура"
    
    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN)

# ========== ПОДПИСКА ==========
async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подписка на обновления"""
    keyboard = [
        [InlineKeyboardButton("✅ 5А класс", callback_data="sub_5a")],
        [InlineKeyboardButton("✅ 5Б класс", callback_data="sub_5b")],
        [InlineKeyboardButton("✅ 6А класс", callback_data="sub_6a")],
        [InlineKeyboardButton("✅ 6Б класс", callback_data="sub_6b")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📢 **Выбери класс для подписки:**\n"
        "Ты будешь получать уведомления об изменениях в расписании.",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

async def subscribe_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка подписки"""
    query = update.callback_query
    await query.answer()
    
    class_name = query.data.replace("sub_", "").upper()
    user_id = query.from_user.id
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Проверяем есть ли уже подписка
    cursor.execute('''
        SELECT * FROM subscriptions 
        WHERE user_id = ? AND class_name = ?
    ''', (user_id, class_name))
    
    if cursor.fetchone():
        await query.edit_message_text(
            f"❌ Ты уже подписан на {class_name} класс",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        # Добавляем подписку на месяц
        from datetime import timedelta
        expires = datetime.now() + timedelta(days=30)
        
        cursor.execute('''
            INSERT INTO subscriptions (user_id, class_name, expires_at, created_at)
            VALUES (?, ?, ?, ?)
        ''', (user_id, class_name, expires, datetime.now()))
        
        cursor.execute('UPDATE users SET subscribed = 1 WHERE user_id = ?', (user_id,))
        conn.commit()
        
        await query.edit_message_text(
            f"✅ Ты подписан на {class_name} класс!\n"
            f"📅 Подписка действует до {expires.strftime('%d.%m.%Y')}",
            parse_mode=ParseMode.MARKDOWN
        )
    
    conn.close()

# ========== АДМИНКА ==========
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Панель администратора"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ У тебя нет прав администратора")
        return
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM users WHERE subscribed = 1')
    subscribed = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM subscriptions')
    total_subs = cursor.fetchone()[0]
    
    conn.close()
    
    text = (
        "👑 **Админ панель**\n\n"
        f"📊 **Статистика:**\n"
        f"• Всего пользователей: {total_users}\n"
        f"• Подписано: {subscribed}\n"
        f"• Всего подписок: {total_subs}\n\n"
        "📢 **Рассылка:**\n"
        "/broadcast текст - разослать всем"
    )
    
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Рассылка сообщений"""
    if update.effective_user.id != ADMIN_ID:
        return
    
    if not context.args:
        await update.message.reply_text("❌ Использование: /broadcast текст")
        return
    
    text = " ".join(context.args)
    await update.message.reply_text(f"📤 Начинаю рассылку...")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    users = cursor.fetchall()
    conn.close()
    
    sent = 0
    failed = 0
    
    for user in users:
        try:
            await context.bot.send_message(
                chat_id=user['user_id'],
                text=f"📢 **Рассылка:**\n\n{text}",
                parse_mode=ParseMode.MARKDOWN
            )
            sent += 1
        except:
            failed += 1
    
    await update.message.reply_text(
        f"✅ **Рассылка завершена**\n"
        f"📨 Отправлено: {sent}\n"
        f"❌ Не удалось: {failed}"
    )

# ========== ПОМОЩЬ ==========
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    text = (
        "📚 **Помощь по командам:**\n\n"
        "/start - начать работу\n"
        "/schedule - расписание\n"
        "/subscribe - подписка на обновления\n"
        "/help - эта справка\n"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# ========== РЕГИСТРАЦИЯ ВСЕХ ХЕНДЛЕРОВ ==========
def register_handlers(app):
    """Регистрирует все обработчики"""
    
    # Команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("schedule", schedule))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("help", help_command))
    
    # Админские команды
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("broadcast", broadcast))
    
    # Callback-запросы (кнопки)
    app.add_handler(CallbackQueryHandler(schedule_callback, pattern="^schedule_"))
    app.add_handler(CallbackQueryHandler(subscribe_callback, pattern="^sub_"))
    
    print("✅ Все обработчики зарегистрированы")