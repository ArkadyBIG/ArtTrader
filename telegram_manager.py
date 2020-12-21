import telebot
from utils import TOKEN
from telebot import ExceptionHandler

_bot = telebot.TeleBot(token=TOKEN)

class Subscriber:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.progress_info_message = None

    def __eq__(self, other):
        return other or self.chat_id == other.chat_id
    
    def __hash__(self):
        return hash(self.chat_id)
    
class _TelegramManager:
    def __init__(self):
        self.subscribers = {Subscriber(-340690791), Subscriber(-490809061)}
        self.max_price = 40
        self._database = None
        
        self._force_parse_command = None
        self._list_command = None
        self._last_parsed_command = None
    
    def set_database(self, db):
        self._database = db
        
    def process_start_command(self, message):
        self.subscribers.add(message.chat.id)
        _bot.send_message(message.chat.id, "I will notify this chat")
        print(message.chat.id)
    
    def process_price_command(self, message):
        if len(message.text) > 15:
            return
        try:
            self.max_price = float(message.text.rsplit('e')[-1])
        except ValueError:
            msg = "Wrong message. Try again."
        else:
            msg = "New price is set to %.2f$" % self.max_price
        _bot.send_message(message.chat.id, msg)

    def send_to_subscribers(self, text, markdown=False):
        markdown = 'MarkdownV2' if markdown else None
        for sub in self.subscribers:

            _bot.send_message(sub.chat_id, text, parse_mode=markdown)
            
    def send_progress_info(self, text, edit_previous=False):
        
        for sub in self.subscribers:
            if edit_previous and sub.progress_info_message is not None:
                try:
                    _bot.edit_message_text(text, sub.chat_id, sub.progress_info_message)
                    continue
                except Exception: pass
            sub.progress_info_message = \
                _bot.send_message(sub.chat_id, text).message_id
    
    def process_parse_command(self, message):
        if self._force_parse_command:
            self._force_parse_command()
    
    def process_list_command(self, msg):
        if self._list_command:
            self._list_command()
    
    def process_last_parse_command(self, msg):
        if self._last_parsed_command:
            self._last_parsed_command()    
    
    def set_force_parse_command(self, command):
        self._force_parse_command = command
        
    def set_list_command(self, command):
        self._list_command = command
        
    def set_last_parsed_command(self, command):
        self._last_parsed_command = command
            
    @classmethod
    def polling(cls):
        _bot.polling()
        
    @classmethod
    def stop(cls):
        _bot.stop_bot()
        

telegram_manager = _TelegramManager()

@_bot.message_handler(commands=['start'])
def process_start_command(message):
    telegram_manager.process_start_command(message)

@_bot.message_handler(func=lambda m: m.text and 'price' in m.text)
def process_price_command(message):
    telegram_manager.process_price_command(message)
    
@_bot.message_handler(commands=['parse'])
def process_parse_command(msg):
    telegram_manager.process_parse_command(msg)

@_bot.message_handler(commands=['list'])
def process_list_command(msg):
    telegram_manager.process_list_command(msg)

@_bot.message_handler(commands=['last_parse'])
def process_last_parse_command(msg):
    telegram_manager.process_last_parse_command(msg)

if __name__ == "__main__":
    telegram_manager.send_to_subscribers('1' * 4100)
