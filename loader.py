# loader.py

from telegram.ext import Updater
from handlers.handlers import CommandHandlers
from api.kinopoisk_api import KinopoiskAPI
from database.database import initialize_database  # Обновлённый путь импорта


class MovieBot:
    def __init__(self, telegram_token, kinopoisk_api_key):
        self.updater = Updater(telegram_token, use_context=True)
        self.dispatcher = self.updater.dispatcher

        # Инициализация базы данных
        initialize_database()

        # Инициализация API клиента
        self.api_client = KinopoiskAPI(kinopoisk_api_key)

        # Инициализация обработчиков
        self.handlers = CommandHandlers(self.api_client, self.dispatcher)
        self.register_handlers()

    def register_handlers(self):
        dp = self.dispatcher

        dp.add_handler(self.handlers.start_handler)
        dp.add_handler(self.handlers.help_handler)

        dp.add_handler(self.handlers.movie_search_handler)
        dp.add_handler(self.handlers.movie_by_rating_handler)
        dp.add_handler(self.handlers.movie_by_budget_handler)

        dp.add_handler(self.handlers.history_handler)  # Добавлен обработчик истории

        dp.add_handler(self.handlers.help_button_handler)
        dp.add_handler(self.handlers.search_by_name_button_handler)
        dp.add_handler(self.handlers.search_by_rating_button_handler)
        dp.add_handler(self.handlers.search_by_budget_button_handler)
        dp.add_handler(self.handlers.back_to_main_handler)
        dp.add_handler(
            self.handlers.history_button_handler
        )  # Добавлен новый обработчик

        dp.add_handler(self.handlers.clear_history_handler)

    def start(self):
        self.updater.start_polling()
        self.updater.idle()
