# handlers/lowprice.py
from telebot import TeleBot
from api.booking_api import get_hotels_by_price


# Обработчик команды /lowprice
def setup_lowprice_handler(bot: TeleBot):
    @bot.message_handler(commands=["lowprice"])
    def lowprice(message):
        bot.reply_to(message, "Введите город для поиска отелей:")

        # Следующее сообщение пользователя будет городом
        @bot.message_handler(func=lambda msg: True)
        def get_city(message):
            city = message.text
            checkin_date = "2024-11-01"  # Можно запросить у пользователя
            checkout_date = "2024-11-05"  # Можно запросить у пользователя

            # Пример получения отелей
            hotels = get_hotels_by_price(city, checkin_date, checkout_date)

            if hotels:
                for hotel in hotels["result"]:
                    bot.send_message(
                        message.chat.id,
                        f"Отель: {hotel['hotel_name']}\nЦена: {hotel['price']['total']} {hotel['price']['currency']}\nСсылка: {hotel['url']}",
                    )
            else:
                bot.reply_to(message, "Не удалось найти отели.")
