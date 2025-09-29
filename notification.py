import schedule
import time
from datetime import datetime, timedelta
import telebot
from telebot import TeleBot

from utils import load_data, parse_time, save_data

def handle_check_notifications(bot: TeleBot):
    # Файл для хранения данных


    while True:
        try:
            current_time = datetime.now()
            
            for user_id, user_notifications in notifications.items():
                notifications_to_remove = []
                
                for i, notification in enumerate(user_notifications):
                    if notification.get('scheduled_time'):
                        scheduled_time = datetime.fromisoformat(notification['scheduled_time'])
                        if current_time >= scheduled_time:
                            try:
                                bot.send_message(user_id, f"🔔 Напоминание: {notification['text']}")
                                notifications_to_remove.append(i)
                            except Exception as e:
                                print(f"Ошибка отправки уведомления: {e}")
                                notifications_to_remove.append(i)
                
                # Удаляем отправленные уведомления
                for i in sorted(notifications_to_remove, reverse=True):
                    user_notifications.pop(i)
                
                if notifications_to_remove:
                    save_data(NOTIFICATIONS_FILE, notifications)
            
            time.sleep(60)  # Проверяем каждую минуту
            
        except Exception as e:
            print(f"Ошибка в check_notifications: {e}")
            time.sleep(60)



def handle_notification_message(message, bot: TeleBot):
    NOTIFICATIONS_FILE = 'notifications.json'
    notifications = load_data(NOTIFICATIONS_FILE)

    user_id = str(message.from_user.id)
    
    # Проверяем, является ли это ответом на создание уведомления
    if message.reply_to_message and 'Создание нового уведомления' in message.reply_to_message.text:
        try:
            if '|' in message.text:
                text_part, time_part = message.text.split('|', 1)
                notification_text = text_part.strip()
                time_str = time_part.strip()
                
                # Простой парсинг времени (можно улучшить)
                notification_time = parse_time(time_str)
                
                if user_id not in notifications:
                    notifications[user_id] = []
                
                notifications[user_id].append({
                    'text': notification_text,
                    'time': time_str,
                    'scheduled_time': notification_time.isoformat() if notification_time else None
                })
                save_data(NOTIFICATIONS_FILE, notifications)
                
                bot.send_message(message.chat.id, f"✅ Уведомление создано!\n📝 {notification_text}\n⏰ {time_str}")
                
            else:
                bot.send_message(message.chat.id, "❌ Неверный формат. Используйте: `текст | время`", parse_mode='Markdown')
                
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")