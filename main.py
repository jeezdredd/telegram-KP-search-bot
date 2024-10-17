import telebot
from dotenv import load_dotenv
import os
from handlers.start_handler import handle_start
from handlers.help_handler import handle_help
from handlers.lowprice_handler import handle_lowprice

# Загрузка конфигурации из .env
load_dotenv()
API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

bot = telebot.TeleBot(API_TOKEN)


# Обработчик команды /start
@bot.message_handler(commands=["start"])
def start_command(message):
    handle_start(bot, message)


# Обработчик команды /help
@bot.message_handler(commands=["help"])
def help_command(message):
    handle_help(bot, message)


# Обработчик команды /lowprice
@bot.message_handler(commands=["lowprice"])
def lowprice_command(message):
    handle_lowprice(bot, message)


if __name__ == "__main__":
    bot.polling(none_stop=True)
