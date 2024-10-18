import config_data.config as config
import telebot

bot = telebot.TeleBot(config.TELEGRAM_TOKEN)


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):  # Название функции не играет никакой роли
    bot.send_message(message.chat.id, message.text)


if __name__ == "__main__":
    bot.infinity_polling()
