# main.py
import os
from dotenv import load_dotenv
import logging
from loader import MovieBot

load_dotenv(".env")
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

if __name__ == "__main__":
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    KINOPOISK_API_KEY = os.getenv("KINOPOISK_API_KEY")

    if not TELEGRAM_TOKEN:
        print("Ошибка: Отсутствует API ключ телеграм бота в файле .env")
        exit(1)
    if not KINOPOISK_API_KEY:
        print("Ошибка: Отсутствует API ключ Кинопоиска в файле .env")
        exit(1)

    movie_bot = MovieBot(TELEGRAM_TOKEN, KINOPOISK_API_KEY)
    movie_bot.start()
