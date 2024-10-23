# database/database.py

import sqlite3
from datetime import datetime
import json
import threading

# Используем Lock для обеспечения потокобезопасности при работе с SQLite
db_lock = threading.Lock()

# Путь к базе данных
DB_PATH = "history.db"


def initialize_database():
    with db_lock:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Создаём таблицу, если она ещё не существует
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                search_type TEXT NOT NULL,
                search_params TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """
        )
        conn.commit()
        conn.close()


def add_search_history(user_id, search_type, search_params):
    """
    Добавляет запись в историю поиска.

    :param user_id: ID пользователя Telegram
    :param search_type: Тип поиска ('name', 'rating', 'budget')
    :param search_params: Параметры поиска в виде словаря
    """
    timestamp = datetime.utcnow().isoformat()
    search_params_json = json.dumps(search_params)
    with db_lock:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO search_history (user_id, search_type, search_params, timestamp)
            VALUES (?, ?, ?, ?)
        """,
            (user_id, search_type, search_params_json, timestamp),
        )
        conn.commit()
        conn.close()


def get_search_history(user_id, limit=20):
    """
    Извлекает историю поиска пользователя.

    :param user_id: ID пользователя Telegram
    :param limit: Максимальное количество записей
    :return: Список записей истории поиска
    """
    with db_lock:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT search_type, search_params, timestamp
            FROM search_history
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
        """,
            (user_id, limit),
        )
        rows = cursor.fetchall()
        conn.close()

    history = []
    for row in rows:
        search_type, search_params_json, timestamp = row
        search_params = json.loads(search_params_json)
        history.append(
            {
                "search_type": search_type,
                "search_params": search_params,
                "timestamp": timestamp,
            }
        )
    return history


def clear_search_history(user_id):
    """
    Очищает историю поиска пользователя.

    :param user_id: ID пользователя Telegram
    """
    with db_lock:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM search_history WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
