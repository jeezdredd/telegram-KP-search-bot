# main.py
import telebot
from handlers.lowprice import setup_lowprice_handler

# Токен
TELEGRAM_TOKEN = "7873288430:AAG0sqt7Mh4QNWIy0XtRGyyMTrZpDO_S_MA"

# Инициализация бота
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Подключение обработчиков команд
setup_lowprice_handler(bot)

# Запуск бота
if __name__ == "__main__":
    bot.polling(none_stop=True)
