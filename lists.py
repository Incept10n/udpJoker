from telebot import types
from telebot import TeleBot

from utils import save_data

def handle_show_my_lists(message, bot: TeleBot, lists):
    markup = types.InlineKeyboardMarkup()
    for list_name in lists:
        markup.add(types.InlineKeyboardButton(
            f"📋 {list_name}", 
            callback_data=f"show_list_{list_name}"
        ))
    
    bot.send_message(message.chat.id, "📂 Ваши списки:", reply_markup=markup)


def handle_show_list_callback(call, lists, bot: TeleBot):
    list_name = call.data.replace('show_list_', '')
    
    if list_name in lists:
        items = lists[list_name]
        if not items:
            bot.send_message(call.message.chat.id, f"📭 Список '{list_name}' пуст.")
            return
        
        response = f"📋 **Список: {list_name}**\n\n"
        for i, item in enumerate(items):
            link_text = f"🔗 {item['link']}" 
            desc_text = item.get('desc', '')  
            if desc_text == '':
                response += f"{i}. {link_text} {desc_text}\n"
            else:
                response += f"{i}. {link_text} - {desc_text}\n"
        
        bot.send_message(call.message.chat.id, response, parse_mode='Markdown')
    else:
        bot.send_message(call.message.chat.id, "❌ Список не найден.")


def handle_list_create_command(message, data, bot: TeleBot):
    try:
        # Разделяем команду и параметры
        command_parts = message.text.split(' ', 2)
        list_name = command_parts[0][1:].lower().strip()  # Убираем / из названия списка
        
        # Если только команда без параметров
        if len(command_parts) == 1:
            if list_name in data:
                # Показываем существующий список
                items = data[list_name]
                if not items:
                    bot.send_message(message.chat.id, f"📭 Список '{list_name}' пуст.")
                    return
                
                response = f"📋 **Список: {list_name}**\n\n"
                for i, item in enumerate(items):
                    link_text = f"🔗 {item['link']}" 
                    desc_text = item.get('desc', '')  
                    if desc_text == '':
                        response += f"{i}. {link_text} {desc_text}\n"
                    else:
                        response += f"{i}. {link_text} - {desc_text}\n"
                
                bot.send_message(message.chat.id, response, parse_mode='Markdown')
            else:
                # Создаем новый пустой список
                data[list_name] = []
                save_data("lists.json", data)
                bot.send_message(message.chat.id, f"✅ Создан новый пустой список '{list_name}'")
            return
        
        # Если есть параметры - создаем список и добавляем элемент
        params_text = command_parts[1] if len(command_parts) == 2 else command_parts[1] + ' ' + command_parts[2]
        
        # Парсим ссылку и описание
        link = None
        description = ""
        
        words = params_text.split()
        if words and (words[0].startswith('http://') or words[0].startswith('https://')):
            link = words[0]
            description = ' '.join(words[1:]) if len(words) > 1 else ""
        else:
            description = params_text
        
        # Создаем новый элемент
        new_item = {}
        if link:
            new_item['link'] = link
        if description:
            new_item['desc'] = description
        
        # Создаем список если его нет
        if list_name not in data:
            data[list_name] = []
        
        # Добавляем элемент в список
        data[list_name].append(new_item)
        save_data("lists.json", data)
        
        # Формируем ответ
        response = f"✅ "
        if list_name not in data:  # Если список был создан только что
            response += f"Создан список '{list_name}' и добавлено:\n"
        else:
            response += f"Добавлено в список '{list_name}':\n"
        
        if link:
            response += f"🔗 {link}\n"
        if description:
            response += f"📝 {description}"
        
        bot.send_message(message.chat.id, response)
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")