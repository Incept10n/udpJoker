import schedule
import time
from datetime import datetime, timedelta
import telebot
from telebot import TeleBot
from telebot import types

from utils import load_data, load_notifications, parse_time, parse_time_to_datetime, save_data, save_notifications

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


def handle_check_notifications(bot_instance : TeleBot):
    """Проверяет и отправляет уведомления"""
    while True:
        try:
            NOTIFICATIONS_FILE = "notifications.json"
            # Загружаем актуальные уведомления
            notifications = load_notifications(NOTIFICATIONS_FILE)
            now = datetime.now()
            sent_notifications = []
            
            # Проходим по всем пользователям и их уведомлениям
            for user_id, user_notifications in notifications.items():
                notifications_to_keep = []
                
                for notification in user_notifications:
                    # Парсим время уведомления
                    notification_time = parse_time_to_datetime(notification['time'])
                    
                    if notification_time:
                        # Проверяем, настало ли время уведомления (допуск ±1 минута)
                        time_diff = (now - notification_time).total_seconds()
                        if -60 <= time_diff <= 60:  # ±1 минута
                            try:
                                # Отправляем уведомление
                                bot_instance.send_message(
                                    int(user_id), 
                                    f"⏰ **Уведомление:** {notification['text']}",
                                    parse_mode='Markdown'
                                )
                                sent_notifications.append({
                                    'user_id': user_id,
                                    'text': notification['text']
                                })
                                # Не добавляем в список для сохранения (удаляем отправленное)
                                continue
                            except Exception as e:
                                print(f"Ошибка отправки уведомления пользователю {user_id}: {e}")
                                # Если ошибка отправки, оставляем уведомление
                                notifications_to_keep.append(notification)
                        else:
                            # Время еще не настало или уже прошло больше минуты, оставляем уведомление
                            notifications_to_keep.append(notification)
                    else:
                        # Не удалось распарсить время, оставляем как есть
                        notifications_to_keep.append(notification)
                
                # Обновляем список уведомлений пользователя
                if notifications_to_keep:
                    notifications[user_id] = notifications_to_keep
                else:
                    # Если уведомлений не осталось, удаляем пользователя
                    if user_id in notifications:
                        del notifications[user_id]
            
            # Сохраняем обновленные уведомления (без отправленных)
            save_notifications(NOTIFICATIONS_FILE, notifications)
            
            # Логируем отправленные уведомления
            if sent_notifications:
                print(f"[{now.strftime('%H:%M:%S')}] Отправлено уведомлений: {len(sent_notifications)}")
                for sent in sent_notifications:
                    print(f"  - Пользователь {sent['user_id']}: {sent['text']}")
            
            # Ждем 30 секунд перед следующей проверкой
            time.sleep(30)
            
        except Exception as e:
            print(f"Ошибка в проверке уведомлений: {e}")
            time.sleep(60)  # При ошибке ждем дольше