# bot.py

from telegram.ext import Updater
from handlers.handlers import CommandHandlers
from api.kinopoisk_api import KinopoiskAPI


class MovieBot:
    def __init__(self, telegram_token, kinopoisk_api_key):
        self.updater = Updater(telegram_token)
        self.dispatcher = self.updater.dispatcher

        # Инициализация API клиента
        self.api_client = KinopoiskAPI(kinopoisk_api_key)

        # Инициализация обработчиков
        self.handlers = CommandHandlers(self.api_client)
        self.register_handlers()

    def register_handlers(self):
        dp = self.dispatcher

        dp.add_handler(self.handlers.start_handler)
        dp.add_handler(self.handlers.help_handler)

        dp.add_handler(self.handlers.movie_search_handler)
        dp.add_handler(self.handlers.movie_by_rating_handler)

        dp.add_handler(self.handlers.help_button_handler)
        dp.add_handler(self.handlers.search_by_name_button_handler)
        dp.add_handler(self.handlers.search_by_rating_button_handler)
        dp.add_handler(self.handlers.back_to_main_handler)

    def start(self):
        self.updater.start_polling()
        self.updater.idle()
