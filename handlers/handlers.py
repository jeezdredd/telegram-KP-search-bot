# handlers.py

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
)
from utils.models import Movie
from database.database import (
    add_search_history,
    get_search_history,
    clear_search_history,
)
import telegram
from datetime import datetime
import locale
from html import escape  # Для экранирования специальных символов

# Устанавливаем локаль для правильного отображения месяцев
try:
    locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")
except locale.Error:
    locale.setlocale(locale.LC_TIME, "")  # Использует системные настройки

# Определение состояний для ConversationHandler
MOVIE_NAME, MOVIE_COUNT = range(2)
MOVIE_RATING, MOVIE_GENRE, MOVIE_RATING_COUNT = range(2, 5)
BUDGET_TYPE, BUDGET_GENRE, BUDGET_COUNT = range(5, 8)


class CommandHandlers:
    """
    Класс для обработки команд и сообщений пользователя.
    """

    def __init__(self, api_client, dispatcher):
        """
        Инициализация обработчиков команд.

        :param api_client: Клиент для взаимодействия с API Кинопоиска.
        :param dispatcher: Диспетчер для регистрации обработчиков.
        """
        self.api_client = api_client
        self.dispatcher = dispatcher

        # Создание обработчиков команд
        self.start_handler = CommandHandler("start", self.start)
        self.help_handler = CommandHandler("help", self.help_command)
        self.history_handler = CommandHandler("history", self.history)

        # Обработчики кнопок
        self.help_button_handler = MessageHandler(
            Filters.regex("^Помощь$"), self.help_command
        )
        self.back_to_main_handler = MessageHandler(
            Filters.regex("^На главную$"), self.start
        )
        self.history_button_handler = MessageHandler(
            Filters.regex("^История поиска$"), self.history
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

        # Обработчик для поиска фильмов по бюджету с учётом жанра
        self.movie_by_budget_handler = ConversationHandler(
            entry_points=[
                CommandHandler("movie_by_budget", self.movie_by_budget),
                MessageHandler(
                    Filters.regex("^Поиск по бюджету$"), self.movie_by_budget
                ),
            ],
            states={
                BUDGET_TYPE: [
                    MessageHandler(Filters.regex("^Отмена$"), self.cancel),
                    MessageHandler(
                        Filters.regex("^(Малобюджетные|Высокобюджетные)$"),
                        self.get_budget_type,
                    ),
                ],
                BUDGET_GENRE: [
                    MessageHandler(Filters.regex("^Отмена$"), self.cancel),
                    MessageHandler(
                        Filters.text & ~Filters.command, self.get_budget_genre
                    ),
                ],
                BUDGET_COUNT: [
                    MessageHandler(Filters.regex("^Отмена$"), self.cancel),
                    MessageHandler(
                        Filters.text & ~Filters.command, self.get_budget_count
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
        self.search_by_budget_button_handler = MessageHandler(
            Filters.regex("^Поиск по бюджету$"), self.movie_by_budget
        )

        # Обработчик для очистки истории
        self.clear_history_handler = CallbackQueryHandler(
            self.handle_clear_history,
            pattern="^(confirm_clear_history|cancel_clear_history)$",
        )

    def register_handlers(self):
        """
        Регистрация всех обработчиков в диспетчере.
        """
        dp = self.dispatcher

        dp.add_handler(self.start_handler)
        dp.add_handler(self.help_handler)

        dp.add_handler(self.movie_search_handler)
        dp.add_handler(self.movie_by_rating_handler)
        dp.add_handler(self.movie_by_budget_handler)

        dp.add_handler(self.history_handler)

        dp.add_handler(self.help_button_handler)
        dp.add_handler(self.search_by_name_button_handler)
        dp.add_handler(self.search_by_rating_button_handler)
        dp.add_handler(self.search_by_budget_button_handler)
        dp.add_handler(self.back_to_main_handler)
        dp.add_handler(self.history_button_handler)

        dp.add_handler(self.clear_history_handler)

    def start(self, update: Update, context: CallbackContext):
        """
        Обработчик команды /start. Отправляет главное меню.
        """
        keyboard = [
            [
                KeyboardButton("Поиск по названию"),
                KeyboardButton("Поиск по рейтингу"),
                KeyboardButton("Поиск по бюджету"),
            ],
            [KeyboardButton("История поиска"), KeyboardButton("Помощь")],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text(
            "👋 Привет! Я бот для поиска фильмов. Выберите действие:",
            reply_markup=reply_markup,
        )

    def cancel(self, update: Update, context: CallbackContext):
        """
        Обработчик команды /cancel или кнопки Отмена. Отправляет главное меню.
        """
        keyboard = [
            [
                KeyboardButton("Поиск по названию"),
                KeyboardButton("Поиск по рейтингу"),
                KeyboardButton("Поиск по бюджету"),
            ],
            [KeyboardButton("История поиска"), KeyboardButton("Помощь")],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text("❌ Действие отменено.", reply_markup=reply_markup)
        return ConversationHandler.END

    def help_command(self, update: Update, context: CallbackContext):
        """
        Обработчик команды /help. Отправляет список доступных команд.
        """
        keyboard = [
            [
                KeyboardButton("Поиск по названию"),
                KeyboardButton("Поиск по рейтингу"),
                KeyboardButton("Поиск по бюджету"),
            ],
            [KeyboardButton("История поиска"), KeyboardButton("На главную")],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        help_text = (
            "📜 <b>Доступные команды:</b>\n\n"
            "/start - Приветственное сообщение\n"
            "/help - Список доступных команд\n"
            "/movie_search - Поиск фильма/сериала по названию\n"
            "/movie_by_rating - Поиск фильмов/сериалов по рейтингу и жанру\n"
            "/movie_by_budget - Поиск фильмов по бюджету и жанру\n"
            "/history - Просмотр истории поиска\n"
        )
        update.message.reply_text(
            help_text, parse_mode="HTML", reply_markup=reply_markup
        )

    # --- Методы для поиска по названию ---

    def movie_search(self, update: Update, context: CallbackContext):
        """
        Начало поиска фильма по названию.
        """
        keyboard = [[KeyboardButton("Отмена")]]
        reply_markup = ReplyKeyboardMarkup(
            keyboard, resize_keyboard=True, one_time_keyboard=True
        )
        update.message.reply_text(
            "🎬 <b>Введите название фильма или сериала:</b>",
            reply_markup=reply_markup,
            parse_mode="HTML",
        )
        return MOVIE_NAME

    def get_movie_name(self, update: Update, context: CallbackContext):
        """
        Сохранение названия фильма и запрос количества результатов.
        """
        name = update.message.text.strip()
        context.user_data["name"] = escape(name)
        update.message.reply_text(
            "🔢 <b>Сколько вариантов вывести?</b> (1-250)", parse_mode="HTML"
        )
        return MOVIE_COUNT

    def get_movie_count(self, update: Update, context: CallbackContext):
        """
        Сохранение количества результатов, получение фильмов из API и отображение.
        """
        count_text = update.message.text.strip()
        try:
            count = int(count_text)
            if count < 1 or count > 250:
                update.message.reply_text(
                    "❌ <b>Пожалуйста, введите число от 1 до 250.</b>",
                    parse_mode="HTML",
                )
                return MOVIE_COUNT

            context.user_data["count"] = count

            # Получение фильмов из API
            movies_data = self.api_client.search_movies_by_name(
                query=context.user_data["name"], limit=context.user_data["count"]
            )

            if not movies_data:
                update.message.reply_text(
                    "🔍 <b>Фильмы не найдены. Попробуйте другой запрос.</b>",
                    parse_mode="HTML",
                )
                return ConversationHandler.END

            movies = [Movie.from_api_data(movie) for movie in movies_data]

            # Запись истории поиска
            add_search_history(
                user_id=update.effective_user.id,
                search_type="name",
                search_params={"name": context.user_data["name"], "count": count},
            )

            # Отправка информации о фильмах пользователю
            for movie in movies:
                self.send_movie_info(update, context, movie)

            # Отправка главного меню после всех результатов
            self.send_main_menu(update, context)

            return ConversationHandler.END

        except ValueError:
            update.message.reply_text(
                "❌ <b>Пожалуйста, введите число.</b>", parse_mode="HTML"
            )
            return MOVIE_COUNT

    # --- Методы для поиска по рейтингу и жанру ---

    def movie_by_rating(self, update: Update, context: CallbackContext):
        """
        Начало поиска фильма по рейтингу.
        """
        keyboard = [[KeyboardButton("Отмена")]]
        reply_markup = ReplyKeyboardMarkup(
            keyboard, resize_keyboard=True, one_time_keyboard=True
        )
        update.message.reply_text(
            "⭐ <b>Введите рейтинг или диапазон рейтингов (например, 7 или 7-9.5):</b>",
            reply_markup=reply_markup,
            parse_mode="HTML",
        )
        return MOVIE_RATING

    def get_rating(self, update: Update, context: CallbackContext):
        """
        Сохранение рейтинга и запрос жанра.
        """
        rating_text = update.message.text.strip()
        try:
            if "-" in rating_text:
                # Пользователь ввёл диапазон
                min_rating_str, max_rating_str = rating_text.replace(" ", "").split("-")
                min_rating = float(min_rating_str)
                max_rating = float(max_rating_str)
            else:
                # Пользователь ввёл одно число
                min_rating = float(rating_text)
                max_rating = 10.0  # Максимальный рейтинг по умолчанию

            # Проверяем корректность введённых значений
            if not (1 <= min_rating <= 10) or not (1 <= max_rating <= 10):
                update.message.reply_text(
                    "❌ <b>Пожалуйста, введите рейтинги в диапазоне от 1 до 10.</b>",
                    parse_mode="HTML",
                )
                return MOVIE_RATING
            if min_rating > max_rating:
                update.message.reply_text(
                    "❌ <b>Минимальный рейтинг не может быть больше максимального.</b>",
                    parse_mode="HTML",
                )
                return MOVIE_RATING

            context.user_data["min_rating"] = min_rating
            context.user_data["max_rating"] = max_rating

            update.message.reply_text(
                "🎨 <b>Введите жанр фильма (например, драма, комедия) или напишите 'любой':</b>",
                parse_mode="HTML",
            )
            return MOVIE_GENRE

        except ValueError:
            update.message.reply_text(
                "❌ <b>Пожалуйста, введите корректный рейтинг или диапазон рейтингов.</b>",
                parse_mode="HTML",
            )
            return MOVIE_RATING

    def get_genre(self, update: Update, context: CallbackContext):
        """
        Сохранение жанра и запрос количества результатов.
        """
        genre_text = update.message.text.strip().lower()
        if genre_text == "любой":
            context.user_data["genre"] = None
        else:
            context.user_data["genre"] = escape(genre_text)
        update.message.reply_text(
            "🔢 <b>Сколько вариантов вывести?</b> (1-250)", parse_mode="HTML"
        )
        return MOVIE_RATING_COUNT

    def get_rating_count(self, update: Update, context: CallbackContext):
        """
        Сохранение количества результатов, получение фильмов из API и отображение.
        """
        count_text = update.message.text.strip()
        try:
            count = int(count_text)
            if count < 1 or count > 250:
                update.message.reply_text(
                    "❌ <b>Пожалуйста, введите число от 1 до 250.</b>",
                    parse_mode="HTML",
                )
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
                    "🔍 <b>Фильмы не найдены. Попробуйте другой запрос.</b>",
                    parse_mode="HTML",
                )
                return ConversationHandler.END

            movies = [Movie.from_api_data(movie) for movie in movies_data]

            # Запись истории поиска
            add_search_history(
                user_id=update.effective_user.id,
                search_type="rating",
                search_params={
                    "min_rating": context.user_data["min_rating"],
                    "max_rating": context.user_data["max_rating"],
                    "genre": context.user_data["genre"],
                    "count": count,
                },
            )

            # Отправка информации о фильмах пользователю
            for movie in movies:
                self.send_movie_info(update, context, movie)

            # Отправка главного меню после всех результатов
            self.send_main_menu(update, context)

            return ConversationHandler.END

        except ValueError:
            update.message.reply_text(
                "❌ <b>Пожалуйста, введите число.</b>", parse_mode="HTML"
            )
            return MOVIE_RATING_COUNT

    # --- Методы для поиска по бюджету и жанру ---

    def movie_by_budget(self, update: Update, context: CallbackContext):
        """
        Начало поиска фильма по бюджету.
        """
        keyboard = [
            [KeyboardButton("Малобюджетные"), KeyboardButton("Высокобюджетные")],
            [KeyboardButton("Отмена")],
        ]
        reply_markup = ReplyKeyboardMarkup(
            keyboard, resize_keyboard=True, one_time_keyboard=True
        )
        update.message.reply_text(
            "💰 <b>Выберите тип бюджета:</b>\n"
            "• <b>Малобюджетные</b> (0-1,500,000 USD)\n"
            "• <b>Высокобюджетные</b> (100,000,000 USD и выше)",
            reply_markup=reply_markup,
            parse_mode="HTML",
        )
        return BUDGET_TYPE

    def get_budget_type(self, update: Update, context: CallbackContext):
        """
        Сохранение типа бюджета и запрос жанра.
        """
        budget_type = update.message.text.strip()
        if budget_type == "Малобюджетные":
            context.user_data["budget_range"] = "0-1500000"
        elif budget_type == "Высокобюджетные":
            context.user_data["budget_range"] = (
                "100000000-1000000000"  # Верхний предел на 1 миллиард
            )
        else:
            update.message.reply_text(
                "❌ <b>Пожалуйста, выберите корректный тип бюджета или нажмите 'Отмена'.</b>",
                parse_mode="HTML",
            )
            return BUDGET_TYPE

        update.message.reply_text(
            "🎨 <b>Введите жанр фильма (например, драма, комедия) или напишите 'любой':</b>",
            parse_mode="HTML",
        )
        return BUDGET_GENRE

    def get_budget_genre(self, update: Update, context: CallbackContext):
        """
        Сохранение жанра и запрос количества результатов.
        """
        genre_text = update.message.text.strip().lower()
        if genre_text == "любой":
            context.user_data["budget_genre"] = None
        else:
            context.user_data["budget_genre"] = escape(genre_text)
        update.message.reply_text(
            "🔢 <b>Сколько вариантов вывести?</b> (1-250)", parse_mode="HTML"
        )
        return BUDGET_COUNT

    def get_budget_count(self, update: Update, context: CallbackContext):
        """
        Сохранение количества результатов, получение фильмов из API и отображение.
        """
        count_text = update.message.text.strip()
        try:
            count = int(count_text)
            if count < 1 or count > 250:
                update.message.reply_text(
                    "❌ <b>Пожалуйста, введите число от 1 до 250.</b>",
                    parse_mode="HTML",
                )
                return BUDGET_COUNT

            context.user_data["count"] = count

            # Получение фильмов из API с учетом жанра и бюджета
            movies_data = self.api_client.search_movies_by_budget(
                budget_range=context.user_data["budget_range"],
                genre=context.user_data["budget_genre"],
                limit=context.user_data["count"],
            )

            if not movies_data:
                update.message.reply_text(
                    "🔍 <b>Фильмы не найдены. Попробуйте другой запрос.</b>",
                    parse_mode="HTML",
                )
                return ConversationHandler.END

            movies = [Movie.from_api_data(movie) for movie in movies_data]

            # Запись истории поиска
            add_search_history(
                user_id=update.effective_user.id,
                search_type="budget",
                search_params={
                    "budget_range": context.user_data["budget_range"],
                    "genre": context.user_data["budget_genre"],
                    "count": count,
                },
            )

            # Отправка информации о фильмах пользователю
            for movie in movies:
                self.send_movie_info(update, context, movie)

            # Отправка главного меню после всех результатов
            self.send_main_menu(update, context)

            return ConversationHandler.END

        except ValueError:
            update.message.reply_text(
                "❌ <b>Пожалуйста, введите число.</b>", parse_mode="HTML"
            )
            return BUDGET_COUNT

    # --- Метод для отправки информации о фильме ---
    def send_movie_info(self, update: Update, context: CallbackContext, movie: Movie):
        """
        Отправляет информацию о фильме пользователю.

        :param update: Объект обновления Telegram.
        :param context: Контекст обратного вызова.
        :param movie: Объект Movie с информацией о фильме.
        """
        # Ограничение длины описания
        max_description_length = 300
        description = movie.description
        if len(description) > max_description_length:
            description = description[:max_description_length].rstrip() + "..."

        # Экранирование всех переменных для предотвращения ошибок HTML-разметки
        title = escape(movie.title)
        description = escape(description)
        rating = escape(str(movie.rating)) if movie.rating else "N/A"
        year = escape(str(movie.year)) if movie.year else "Неизвестно"
        genres = escape(", ".join(movie.genres))
        age_rating = escape(str(movie.age_rating)) if movie.age_rating else "N/A"
        budget = (
            escape(f"${int(movie.budget):,}".replace(",", " "))
            if movie.budget
            else None
        )

        # Формирование сообщения
        message = (
            f"📌 <b>Название:</b> {title}\n"
            f"📝 <b>Описание:</b> {description}\n"
            f"⭐ <b>Рейтинг:</b> {rating}\n"
            f"📅 <b>Год:</b> {year}\n"
            f"🎭 <b>Жанр:</b> {genres}\n"
            f"🔞 <b>Возрастной рейтинг:</b> {age_rating}+\n"
        )

        # Добавление бюджета, если доступно
        if budget:
            message += f"💸 <b>Бюджет:</b> {budget}\n"

        # Проверка длины сообщения
        if len(message) > 1024:
            message = message[:1021].rstrip() + "..."

        if movie.poster_url:
            try:
                context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=movie.poster_url,
                    caption=message,
                    parse_mode="HTML",
                )
            except telegram.error.BadRequest as e:
                # Если сообщение слишком длинное, отправляем без описания и бюджета
                if "Message caption is too long" in str(e):
                    message = (
                        f"📌 <b>Название:</b> {title}\n"
                        f"⭐ <b>Рейтинг:</b> {rating}\n"
                        f"📅 <b>Год:</b> {year}\n"
                        f"🎭 <b>Жанр:</b> {genres}\n"
                        f"🔞 <b>Возрастной рейтинг:</b> {age_rating}+"
                    )
                    if budget:
                        message += f"\n💸 <b>Бюджет:</b> {budget}"
                    if len(message) > 1024:
                        message = message[:1021].rstrip() + "..."
                    context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=movie.poster_url,
                        caption=message,
                        parse_mode="HTML",
                    )
                else:
                    update.message.reply_text(
                        "❌ <b>Произошла ошибка при отправке информации о фильме. Пожалуйста, попробуйте позже.</b>",
                        parse_mode="HTML",
                    )
        else:
            try:
                update.message.reply_text(message, parse_mode="HTML")
            except telegram.error.BadRequest as e:
                # Если сообщение слишком длинное, отправляем его частями или сокращаем
                if "too long" in str(e).lower():
                    for i in range(0, len(message), 1024):
                        update.message.reply_text(
                            message[i : i + 1024], parse_mode="HTML"
                        )
                else:
                    update.message.reply_text(
                        "❌ <b>Произошла ошибка при отправке информации о фильме. Пожалуйста, попробуйте позже.</b>",
                        parse_mode="HTML",
                    )

    # --- Метод для отправки главного меню ---
    def send_main_menu(self, update: Update, context: CallbackContext):
        """
        Отправляет главное меню пользователю.
        """
        keyboard = [
            [
                KeyboardButton("Поиск по названию"),
                KeyboardButton("Поиск по рейтингу"),
                KeyboardButton("Поиск по бюджету"),
            ],
            [KeyboardButton("История поиска"), KeyboardButton("Помощь")],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text(
            "🔄 <b>Выберите следующее действие:</b>",
            reply_markup=reply_markup,
            parse_mode="HTML",
        )

    # --- Метод для отображения истории поиска ---
    def history(self, update: Update, context: CallbackContext):
        """
        Отправляет пользователю историю поиска с возможностью очистки.
        """
        user_id = update.effective_user.id
        history = get_search_history(user_id)

        if not history:
            update.message.reply_text(
                "📭 <b>Ваша история поиска пуста.</b>", parse_mode="HTML"
            )
            return

        message_lines = ["📚 <b>Ваша история поиска:</b>"]
        for entry in history:
            search_type = entry["search_type"]
            params = entry["search_params"]
            timestamp_iso = entry["timestamp"]

            # Форматирование времени
            try:
                timestamp = datetime.fromisoformat(timestamp_iso).strftime(
                    "%d.%m.%Y %H:%M"
                )
            except ValueError:
                timestamp = escape(
                    timestamp_iso
                )  # Экранирование, если формат некорректен

            # Форматирование строки поиска
            if search_type == "name":
                name = escape(params.get("name", "N/A"))
                count = escape(str(params.get("count", "N/A")))
                message_lines.append(
                    f"📖 Поиск по названию:\n"
                    f"• Название: {name}\n"
                    f"• Количество: {count}\n"
                    f"• Время: {timestamp}\n"
                )
            elif search_type == "rating":
                min_rating = escape(str(params.get("min_rating", "N/A")))
                max_rating = escape(str(params.get("max_rating", "N/A")))
                genre = escape(params.get("genre", "любой"))
                count = escape(str(params.get("count", "N/A")))
                message_lines.append(
                    f"⭐ Поиск по рейтингу:\n"
                    f"• Рейтинг: {min_rating}-{max_rating}\n"
                    f"• Жанр: {genre}\n"
                    f"• Количество: {count}\n"
                    f"• Время: {timestamp}\n"
                )
            elif search_type == "budget":
                budget_range = escape(params.get("budget_range", "N/A"))
                genre = escape(params.get("genre", "любой"))
                count = escape(str(params.get("count", "N/A")))
                message_lines.append(
                    f"💰 Поиск по бюджету:\n"
                    f"• Бюджет: {budget_range}\n"
                    f"• Жанр: {genre}\n"
                    f"• Количество: {count}\n"
                    f"• Время: {timestamp}\n"
                )

        # Ограничение длины сообщения Telegram (4096 символов)
        full_message = "\n".join(message_lines)
        if len(full_message) > 4096:
            for i in range(0, len(full_message), 4096):
                update.message.reply_text(full_message[i : i + 4096], parse_mode="HTML")
        else:
            # Добавление кнопок для очистки истории
            keyboard = [
                [
                    InlineKeyboardButton(
                        "✅ Да, очистить", callback_data="confirm_clear_history"
                    ),
                    InlineKeyboardButton(
                        "❌ Нет, не очищать",
                        callback_data="cancel_clear_history",
                    ),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(full_message, reply_markup=reply_markup)

    # --- Метод для обработки очистки истории и подтверждения ---
    def handle_clear_history(self, update: Update, context: CallbackContext):
        """
        Обрабатывает подтверждение очистки истории поиска.
        """
        query = update.callback_query
        query.answer()

        data = query.data

        if data == "confirm_clear_history":
            user_id = query.from_user.id
            clear_search_history(user_id)
            query.edit_message_text(
                "🗑️ Ваша история поиска успешно очищена.",
            )
        elif data == "cancel_clear_history":
            query.edit_message_text(
                "ℹ️ Очистка истории поиска отменена.",
            )
