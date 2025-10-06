from telebot import TeleBot

def handlel_send_help(message, bot: TeleBot):
    help_text = """
📖 **Доступные команды:**

**Работа со списками:**
`/technic [ссылка] [описание]` - добавить в список "technic"
`/books [ссылка] [описание]` - добавить в список "books"  
`/films [ссылка] [описание]` - добавить в список "films"
`/mylists` - посмотреть все ваши списки

**Уведомления:**
`/newnotification` - создать новое уведомление
`/mynotifications` - мои уведомления

**Примеры:**
`/technic https://example.com Крутой гаджет`
`/books https://book.com Интересная книга`
`/films` - покажет список фильмов
"""
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')