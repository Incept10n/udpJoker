import telebot
from telebot import types
import json
import os
import threading
from datetime import datetime, timedelta
from help import handlel_send_help
from lists import handle_show_my_lists
from notification import handle_check_notifications, handle_notification_message
from utils import load_data


TELEGRAM_API_TOKEN = os.environ['TELEGRAM_API_TOKEN']
# Инициализация бота
bot = telebot.TeleBot(TELEGRAM_API_TOKEN)

# Файлы для хранения данных
USERS_FILE = 'users.json'
LISTS_FILE = 'lists.json'
NOTIFICATIONS_FILE = 'notifications.json'

# Инициализация данных
notifications = load_data(NOTIFICATIONS_FILE)
users = load_data(USERS_FILE)
lists = load_data(LISTS_FILE)

# Команда старт
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # user_id = str(message.from_user.id)
    
    # if user_id not in users:
    #     users[user_id] = {
    #         'username': message.from_user.username,
    #         'first_name': message.from_user.first_name,
    #         'lists': {}
    #     }
    #     save_data(USERS_FILE, users)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('/help')
    btn2 = types.KeyboardButton('/mylists')
    btn3 = types.KeyboardButton('/newnotification')
    btn4 = types.KeyboardButton('/mynotifications')
    markup.add(btn1, btn2, btn3, btn4)
    
    bot.send_message(message.chat.id, 
                    "👋 Привет! Я бот для управления списками и уведомлениями.\n\n"
                    "📝 Создавайте списки командой /[название списка]\n"
                    "🔔 Настраивайте уведомления командой /newnotification\n"
                    "📋 Смотрите свои списки командой /mylists\n\n"
                    "Для справки используйте /help", 
                    reply_markup=markup)

# Команда помощи
@bot.message_handler(commands=['help'])
def send_help(message):
    handlel_send_help(message, bot)

# Динамическое создание команд для списков
@bot.message_handler(commands=['mylists'])
def show_my_lists(message):
    handle_show_my_lists(message, bot, lists)

# Обработчик для показа конкретного списка
@bot.callback_query_handler(func=lambda call: call.data.startswith('show_list_'))
def show_list_callback(call):
    list_name = call.data.replace('show_list_', '')
    user_id = str(call.from_user.id)
    
    if user_id in users and list_name in users[user_id]['lists']:
        items = users[user_id]['lists'][list_name]
        if not items:
            bot.send_message(call.message.chat.id, f"📭 Список '{list_name}' пуст.")
            return
        
        response = f"📋 **Список: {list_name}**\n\n"
        for i, item in enumerate(items, 1):
            response += f"{i}. {'🔗 ' + item['link'] + ' - ' if item.get('link') else ''}{item.get('description', '')}\n"
        
        bot.send_message(call.message.chat.id, response, parse_mode='Markdown')
    else:
        bot.send_message(call.message.chat.id, "❌ Список не найден.")

# Динамический обработчик для всех команд-списков
@bot.message_handler(func=lambda message: message.text.startswith('/') and not message.text.startswith('/start') and not message.text.startswith('/help') and not message.text.startswith('/mylists') and not message.text.startswith('/new') and not message.text.startswith('/my'))
def handle_list_command(message):
    try:
        command_parts = message.text.split(' ', 2)
        list_name = command_parts[0][1:].lower()  # Убираем / из начала
        
        user_id = str(message.from_user.id)
        
        # Инициализация пользователя если нужно
        if user_id not in users:
            users[user_id] = {
                'username': message.from_user.username,
                'first_name': message.from_user.first_name,
                'lists': {}
            }
        
        # Инициализация списка если нужно
        if list_name not in users[user_id]['lists']:
            users[user_id]['lists'][list_name] = []
        
        # Если только команда без параметров - показываем список
        if len(command_parts) == 1:
            items = users[user_id]['lists'][list_name]
            if not items:
                bot.send_message(message.chat.id, f"📭 Список '{list_name}' пуст.")
                return
            
            response = f"📋 **Список: {list_name}**\n\n"
            for i, item in enumerate(items, 1):
                link_part = f"🔗 {item['link']} - " if item.get('link') else ""
                response += f"{i}. {link_part}{item.get('description', '')}\n"
            
            bot.send_message(message.chat.id, response, parse_mode='Markdown')
            return
        
        # Добавление элемента в список
        link = None
        description = ""
        
        # Парсим ссылку и описание
        if len(command_parts) >= 2:
            text_after_command = ' '.join(command_parts[1:])
            words = text_after_command.split()
            
            # Проверяем первое слово на ссылку
            if words and (words[0].startswith('http://') or words[0].startswith('https://')):
                link = words[0]
                description = ' '.join(words[1:]) if len(words) > 1 else ""
            else:
                description = text_after_command
        
        new_item = {}
        if link:
            new_item['link'] = link
        if description:
            new_item['description'] = description
        
        users[user_id]['lists'][list_name].append(new_item)
        save_data(USERS_FILE, users)
        
        response = f"✅ Добавлено в список '{list_name}':\n"
        if link:
            response += f"🔗 {link}\n"
        if description:
            response += f"📝 {description}"
        
        bot.send_message(message.chat.id, response)
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")

# Управление уведомлениями
@bot.message_handler(commands=['newnotification'])
def new_notification(message):
    user_id = str(message.from_user.id)
    
    if user_id not in notifications:
        notifications[user_id] = []
    
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

@bot.message_handler(commands=['mynotifications'])
def show_notifications(message):
    user_id = str(message.from_user.id)
    
    if user_id not in notifications or not notifications[user_id]:
        bot.send_message(message.chat.id, "🔕 У вас нет активных уведомлений.")
        return
    
    response = "⏰ **Ваши уведомления:**\n\n"
    for i, notification in enumerate(notifications[user_id], 1):
        response += f"{i}. {notification['text']} - {notification['time']}\n"
    
    bot.send_message(message.chat.id, response, parse_mode='Markdown')

# Обработчик текстовых сообщений для уведомлений
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text(message):
    handle_notification_message(message, bot)

# Функция для парсинга времени (упрощенная)

def check_notifications():
    handle_check_notifications(bot)

# Запуск проверки уведомлений в отдельном потоке
def start_notification_checker():
    thread = threading.Thread(target=check_notifications, daemon=True)
    thread.start()

if __name__ == "__main__":
    print("Бот запущен...")
    start_notification_checker()
    bot.polling(none_stop=True)