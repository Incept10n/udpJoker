import schedule
import time
from datetime import datetime, timedelta
import telebot
from telebot import TeleBot
from telebot import types

from utils import load_data, load_notifications, parse_time, save_data, save_notifications

def new_notification_handler(message, bot: TeleBot):
    markup = types.ForceReply(selective=False)
    bot.send_message(message.chat.id, 
                    "⏰ Создание нового уведомления.\n"
                    "Введите текст уведомления и время в формате:\n"
                    "`текст уведомления | время`\n\n"
                    "Примеры времени:\n"
                    "• `15:30` - сегодня в 15:30\n"
                    "• `14:25 25.12` - 25 декабря в 14:25\n"
                    "• `через 2 часа` - через 2 часа\n"
                    "• `через 30 минут` - через 30 минут", 
                    parse_mode='Markdown', reply_markup=markup)


def show_notifications_handler(message, bot: TeleBot, notifications: dict):
    NOTIFICATIONS_FILE = "notifications.json"
    user_id = str(message.from_user.id)
    
    # Загружаем актуальные данные
    notifications = load_notifications(NOTIFICATIONS_FILE)
    
    if user_id not in notifications or not notifications[user_id]:
        bot.send_message(message.chat.id, "🔕 У вас нет активных уведомлений.")
        return
    
    response = "⏰ **Ваши уведомления:**\n\n"
    for i, notification in enumerate(notifications[user_id], 1):
        response += f"{i}. {notification['text']} - {notification['time']}\n"
    
    bot.send_message(message.chat.id, response, parse_mode='Markdown')


def handle_notification_reply(message, bot: TeleBot):
    NOTIFICATIONS_FILE = "notifications.json"
    try:
        user_id = str(message.from_user.id)
        text = message.text.strip()
        
        # Разделяем текст и время
        if '|' not in text:
            bot.send_message(message.chat.id, "❌ Используйте формат: `текст | время`", parse_mode='Markdown')
            return
        
        notification_text, time_str = [part.strip() for part in text.split('|', 1)]
        
        # Парсим время
        parsed_time = parse_time(time_str)
        if not parsed_time:
            bot.send_message(message.chat.id, "❌ Неверный формат времени. Используйте примеры из инструкции.")
            return
        
        # Загружаем текущие уведомления
        notifications = load_notifications(NOTIFICATIONS_FILE)
        
        # Инициализируем список уведомлений для пользователя
        if user_id not in notifications:
            notifications[user_id] = []
        
        # Добавляем новое уведомление
        new_notif = {
            "text": notification_text,
            "time": parsed_time
        }
        notifications[user_id].append(new_notif)
        
        # Сохраняем
        save_notifications(NOTIFICATIONS_FILE, notifications)
        
        bot.send_message(message.chat.id, f"✅ Уведомление создано!\n📝 {notification_text}\n⏰ {parsed_time}")
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")































