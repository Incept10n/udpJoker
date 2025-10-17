import time
from datetime import datetime
from telebot import TeleBot
from telebot import types
import pytz

from utils import load_notifications, parse_time, parse_time_to_datetime, save_notifications

def new_notification_handler(message, bot: TeleBot):
    markup = types.ForceReply(selective=False)
    bot.send_message(message.chat.id, 
                    "⏰ Создание нового уведомления.\n"
                    "Введите текст уведомления и время в формате:\n"
                    "`текст уведомления | время`\n\n"
                    "Примеры времени:\n"
                    "• `15:30` - сегодня в 15:30 (МСК)\n"
                    "• `14:25 25.12` - 25 декабря в 14:25 (МСК)\n"
                    "• `через 2 часа` - через 2 часа (МСК)\n"
                    "• `через 30 минут` - через 30 минут (МСК)", 
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
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('/help')
    btn2 = types.KeyboardButton('/mylists')
    btn3 = types.KeyboardButton('/newnotification')
    btn4 = types.KeyboardButton('/mynotifications')
    markup.add(btn1, btn2, btn3, btn4)

    NOTIFICATIONS_FILE = "notifications.json"

    try:
        user_id = str(message.from_user.id)
        text = message.text.strip()
        
        # Разделяем текст и время
        if '|' not in text:
            bot.send_message(message.chat.id, "❌ Используйте формат: `текст | время`", parse_mode='Markdown', reply_markup=markup)
            return
        
        notification_text, time_str = [part.strip() for part in text.split('|', 1)]
        
        # Парсим время
        parsed_time = parse_time(time_str)
        if not parsed_time:
            bot.send_message(message.chat.id, "❌ Неверный формат времени. Используйте примеры из инструкции.", reply_markup=markup)
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
        
        bot.send_message(message.chat.id, f"✅ Уведомление создано!\n📝 {notification_text}\n⏰ {parsed_time}", reply_markup=markup)
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}", reply_markup=markup)


def handle_check_notifications(bot_instance: TeleBot):
    """Проверяет и отправляет уведомления"""
    moscow_tz = pytz.timezone('Europe/Moscow')

    while True:
        try:
            NOTIFICATIONS_FILE = "notifications.json"
            notifications = load_notifications(NOTIFICATIONS_FILE)
            now = datetime.now(moscow_tz)
            sent_notifications = []
            
            # Create a new dictionary for updated notifications
            updated_notifications = {}
            
            for user_id, user_notifications in notifications.items():
                notifications_to_keep = []
                
                for notification in user_notifications:
                    notification_time = parse_time_to_datetime(notification['time'], moscow_tz)
                    
                    if notification_time:
                        time_diff = (now - notification_time).total_seconds()
                        if -30 <= time_diff <= 30:
                            try:
                                bot_instance.send_message(
                                    int(user_id), 
                                    f"⏰ **Уведомление:** {notification['text']}",
                                    parse_mode='Markdown'
                                )
                                sent_notifications.append({
                                    'user_id': user_id,
                                    'text': notification['text']
                                })
                                continue
                            except Exception as e:
                                print(f"Ошибка отправки уведомления пользователю {user_id}: {e}")
                                notifications_to_keep.append(notification)
                        else:
                            notifications_to_keep.append(notification)
                    else:
                        notifications_to_keep.append(notification)
                
                # Only keep users who still have notifications
                if notifications_to_keep:
                    updated_notifications[user_id] = notifications_to_keep
            
            # Replace the old notifications with the updated ones
            notifications = updated_notifications
            save_notifications(NOTIFICATIONS_FILE, notifications)
            
            if sent_notifications:
                print(f"[{now.strftime('%H:%M:%S')} МСК] Отправлено уведомлений: {len(sent_notifications)}")
                for sent in sent_notifications:
                    print(f"  - Пользователь {sent['user_id']}: {sent['text']}")
            
            time.sleep(15)
            
        except Exception as e:
            print(f"Ошибка в проверке уведомлений: {e}")
            time.sleep(60)