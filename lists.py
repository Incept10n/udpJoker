def handle_show_my_lists(message, bot):
    
    
    if user_id not in users or not users[user_id]['lists']:
        bot.send_message(message.chat.id, "📭 У вас пока нет списков.")
        return
    
    markup = types.InlineKeyboardMarkup()
    for list_name in users[user_id]['lists'].keys():
        markup.add(types.InlineKeyboardButton(
            f"📋 {list_name}", 
            callback_data=f"show_list_{list_name}"
        ))
    
    bot.send_message(message.chat.id, "📂 Ваши списки:", reply_markup=markup)