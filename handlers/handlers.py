# handlers.py

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    Filters,
)
from utils.models import Movie

# Определение состояний для ConversationHandler
MOVIE_NAME, MOVIE_COUNT = range(2)
MOVIE_RATING, MOVIE_GENRE, MOVIE_RATING_COUNT = range(2, 5)


class CommandHandlers:
    def __init__(self, api_client):
        self.api_client = api_client

        # Создание обработчиков команд
        self.start_handler = CommandHandler("start", self.start)
        self.help_handler = CommandHandler("help", self.help_command)

        # Обработчики кнопок
        self.help_button_handler = MessageHandler(
            Filters.regex("^Помощь$"), self.help_command
        )
        self.back_to_main_handler = MessageHandler(
            Filters.regex("^На главную$"), self.start
        )

        # Обработчик для поиска фильмов по названию
        self.movie_search_handler = ConversationHandler(
            entry_points=[
                CommandHandler("movie_search", self.movie_search),
                MessageHandler(Filters.regex("^Поиск по названию$"), self.movie_search),
            ],
            states={
                MOVIE_NAME: [
                    MessageHandler(Filters.regex("^Отмена$"), self.cancel),
                    MessageHandler(
                        Filters.text & ~Filters.command, self.get_movie_name
                    ),
                ],
                MOVIE_COUNT: [
                    MessageHandler(Filters.regex("^Отмена$"), self.cancel),
                    MessageHandler(
                        Filters.text & ~Filters.command, self.get_movie_count
                    ),
                ],
            },
            fallbacks=[
                CommandHandler("cancel", self.cancel),
                MessageHandler(Filters.regex("^Отмена$"), self.cancel),
            ],
        )

        # Обработчик для поиска фильмов по рейтингу с учётом жанра
        self.movie_by_rating_handler = ConversationHandler(
            entry_points=[
                CommandHandler("movie_by_rating", self.movie_by_rating),
                MessageHandler(
                    Filters.regex("^Поиск по рейтингу$"), self.movie_by_rating
                ),
            ],
            states={
                MOVIE_RATING: [
                    MessageHandler(Filters.regex("^Отмена$"), self.cancel),
                    MessageHandler(Filters.text & ~Filters.command, self.get_rating),
                ],
                MOVIE_GENRE: [
                    MessageHandler(Filters.regex("^Отмена$"), self.cancel),
                    MessageHandler(Filters.text & ~Filters.command, self.get_genre),
                ],
                MOVIE_RATING_COUNT: [
                    MessageHandler(Filters.regex("^Отмена$"), self.cancel),
                    MessageHandler(
                        Filters.text & ~Filters.command, self.get_rating_count
                    ),
                ],
            },
            fallbacks=[
                CommandHandler("cancel", self.cancel),
                MessageHandler(Filters.regex("^Отмена$"), self.cancel),
            ],
        )

        # Обработчики кнопок для быстрого доступа
        self.search_by_name_button_handler = MessageHandler(
            Filters.regex("^Поиск по названию$"), self.movie_search
        )
        self.search_by_rating_button_handler = MessageHandler(
            Filters.regex("^Поиск по рейтингу$"), self.movie_by_rating
        )

    def start(self, update: Update, context: CallbackContext):
        keyboard = [
            [KeyboardButton("Поиск по названию"), KeyboardButton("Поиск по рейтингу")],
            [KeyboardButton("Помощь")],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text(
            "Привет! Я бот для поиска фильмов. Выберите действие:",
            reply_markup=reply_markup,
        )

    def cancel(self, update: Update, context: CallbackContext):
        keyboard = [
            [KeyboardButton("Поиск по названию"), KeyboardButton("Поиск по рейтингу")],
            [KeyboardButton("Помощь")],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text("Действие отменено.", reply_markup=reply_markup)
        return ConversationHandler.END

    def help_command(self, update: Update, context: CallbackContext):
        keyboard = [
            [KeyboardButton("Поиск по названию"), KeyboardButton("Поиск по рейтингу")],
            [KeyboardButton("На главную")],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        help_text = (
            "Доступные команды:\n"
            "/start - Приветственное сообщение\n"
            "/help - Список доступных команд\n"
            "/movie_search - Поиск фильма/сериала по названию\n"
            "/movie_by_rating - Поиск фильмов/сериалов по рейтингу и жанру\n"
        )
        update.message.reply_text(help_text, reply_markup=reply_markup)

    def movie_search(self, update: Update, context: CallbackContext):
        keyboard = [[KeyboardButton("Отмена")]]
        reply_markup = ReplyKeyboardMarkup(
            keyboard, resize_keyboard=True, one_time_keyboard=True
        )
        update.message.reply_text(
            "Введите название фильма или сериала:", reply_markup=reply_markup
        )
        return MOVIE_NAME

    def get_movie_name(self, update: Update, context: CallbackContext):
        name = update.message.text.strip()
        context.user_data["name"] = name
        update.message.reply_text("Сколько вариантов вывести? (1-250)")
        return MOVIE_COUNT

    def get_movie_count(self, update: Update, context: CallbackContext):
        count_text = update.message.text.strip()
        try:
            count = int(count_text)
            if count < 1 or count > 250:
                update.message.reply_text("Пожалуйста, введите число от 1 до 250.")
                return MOVIE_COUNT

            context.user_data["count"] = count

            # Получение фильмов из API
            movies_data = self.api_client.search_movies_by_name(
                query=context.user_data["name"], limit=context.user_data["count"]
            )

            if not movies_data:
                update.message.reply_text(
                    "Фильмы не найдены. Попробуйте другой запрос."
                )
                return ConversationHandler.END

            movies = [Movie.from_api_data(movie) for movie in movies_data]

            # Отправка информации о фильмах пользователю
            for movie in movies:
                self.send_movie_info(update, context, movie)

            return ConversationHandler.END

        except ValueError:
            update.message.reply_text("Пожалуйста, введите число.")
            return MOVIE_COUNT

    def send_movie_info(self, update: Update, context: CallbackContext, movie: Movie):
        message = (
            f"*Название:* {movie.title}\n"
            f"*Описание:* {movie.description}\n"
            f"*Рейтинг:* {movie.rating}\n"
            f"*Год:* {movie.year}\n"
            f"*Жанр:* {', '.join(movie.genres)}\n"
            f"*Возрастной рейтинг:* {movie.age_rating if movie.age_rating else 'N/A'}+"
        )
        keyboard = [
            [KeyboardButton("Поиск по названию"), KeyboardButton("Поиск по рейтингу")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        if movie.poster_url:
            context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=movie.poster_url,
                caption=message,
                parse_mode="Markdown",
                reply_markup=reply_markup,
            )
        else:
            update.message.reply_text(
                message, parse_mode="Markdown", reply_markup=reply_markup
            )

    # Handlers для поиска фильмов по рейтингу и жанру
    def movie_by_rating(self, update: Update, context: CallbackContext):
        keyboard = [[KeyboardButton("Отмена")]]
        reply_markup = ReplyKeyboardMarkup(
            keyboard, resize_keyboard=True, one_time_keyboard=True
        )
        update.message.reply_text(
            "Введите рейтинг или диапазон рейтингов (например, 7 или 7-9.5):",
            reply_markup=reply_markup,
        )
        return MOVIE_RATING

    def get_rating(self, update: Update, context: CallbackContext):
        rating_text = update.message.text.strip()
        try:
            if "-" in rating_text:
                # Пользователь ввёл диапазон
                min_rating_str, max_rating_str = rating_text.split("-")
                min_rating = float(min_rating_str)
                max_rating = float(max_rating_str)
            else:
                # Пользователь ввёл одно число
                min_rating = float(rating_text)
                max_rating = 10.0  # Максимальный рейтинг по умолчанию

            # Проверяем корректность введённых значений
            if not (1 <= min_rating <= 10) or not (1 <= max_rating <= 10):
                update.message.reply_text(
                    "Пожалуйста, введите рейтинги в диапазоне от 1 до 10."
                )
                return MOVIE_RATING
            if min_rating > max_rating:
                update.message.reply_text(
                    "Минимальный рейтинг не может быть больше максимального."
                )
                return MOVIE_RATING

            context.user_data["min_rating"] = min_rating
            context.user_data["max_rating"] = max_rating

            update.message.reply_text(
                "Введите жанр фильма (например, драма, комедия) или напишите 'любой':"
            )
            return MOVIE_GENRE

        except ValueError:
            update.message.reply_text(
                "Пожалуйста, введите корректный рейтинг или диапазон рейтингов."
            )
            return MOVIE_RATING

    def get_genre(self, update: Update, context: CallbackContext):
        genre_text = update.message.text.strip().lower()
        if genre_text == "любой":
            context.user_data["genre"] = None
        else:
            context.user_data["genre"] = genre_text
        update.message.reply_text("Сколько вариантов вывести? (1-250)")
        return MOVIE_RATING_COUNT

    def get_rating_count(self, update: Update, context: CallbackContext):
        count_text = update.message.text.strip()
        try:
            count = int(count_text)
            if count < 1 or count > 250:
                update.message.reply_text("Пожалуйста, введите число от 1 до 250.")
                return MOVIE_RATING_COUNT

            context.user_data["count"] = count

            # Получение фильмов из API с учетом жанра
            movies_data = self.api_client.search_movies_by_rating(
                min_rating=context.user_data["min_rating"],
                max_rating=context.user_data["max_rating"],
                genre=context.user_data["genre"],
                limit=context.user_data["count"],
            )

            if not movies_data:
                update.message.reply_text(
                    "Фильмы не найдены. Попробуйте другой запрос."
                )
                return ConversationHandler.END

            movies = [Movie.from_api_data(movie) for movie in movies_data]

            # Отправка информации о фильмах пользователю
            for movie in movies:
                self.send_movie_info(update, context, movie)

            return ConversationHandler.END

        except ValueError:
            update.message.reply_text("Пожалуйста, введите число.")
            return MOVIE_RATING_COUNT
