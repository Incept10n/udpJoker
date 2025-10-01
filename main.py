import telebot
from telebot import types
import json
import os
import threading
from datetime import datetime, timedelta
from help import handlel_send_help
from lists import handle_list_create_command, handle_show_list_callback, handle_show_my_lists
from notification import handle_check_notifications, handle_notification_reply, new_notification_handler, show_notifications_handler
from utils import load_data


TELEGRAM_API_TOKEN = os.environ['TELEGRAM_API_TOKEN']
# Инициализация бота
bot = telebot.TeleBot(TELEGRAM_API_TOKEN)

# Файлы для хранения данных
LISTS_FILE = 'lists.json'
NOTIFICATIONS_FILE = 'notifications.json'

# Инициализация данных
notifications = load_data(NOTIFICATIONS_FILE)
lists = load_data(LISTS_FILE)

# Команда старт
@bot.message_handler(commands=['start'])
def send_welcome(message):
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
    handle_show_list_callback(call, lists, bot)

# Динамический обработчик для всех команд-списков (создание)
@bot.message_handler(func=lambda message: message.text.startswith('/') and not message.text.startswith('/start') and not message.text.startswith('/help') and not message.text.startswith('/mylists') and not message.text.startswith('/newnotification') and not message.text.startswith('/mynotifications'))
def handle_list_command(message):
    handle_list_create_command(message, lists, bot)

# Управление уведомлениями
@bot.message_handler(commands=['newnotification'])
def new_notification(message):
    new_notification_handler(message, bot)

# Обработчик ответа на ForceReply
@bot.message_handler(func=lambda message: message.reply_to_message is not None and 
                      "Создание нового уведомления" in message.reply_to_message.text)
def notification_reply(message):
    handle_notification_reply(message, bot)


@bot.message_handler(commands=['mynotifications'])
def show_notifications(message):
    show_notifications_handler(message, bot, notifications)


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