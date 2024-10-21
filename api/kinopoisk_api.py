# kinopoisk_api.py

import requests


class KinopoiskAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.kinopoisk.dev"

    def search_movies_by_name(self, query, page=1, limit=10):
        url = f"{self.base_url}/v1.4/movie/search"
        headers = {"X-API-KEY": self.api_key}
        params = {"query": query, "page": page, "limit": limit}
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Проверка успешности запроса
            data = response.json()
            return data.get("docs", [])
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к API Кинопоиска: {e}")
            return []

    def search_movies_by_rating(
        self, min_rating, max_rating, genre=None, page=1, limit=10
    ):
        url = f"{self.base_url}/v1.4/movie"
        headers = {"X-API-KEY": self.api_key, "accept": "application/json"}
        params = {
            "rating.kp": f"{min_rating}-{max_rating}",
            "page": page,
            "limit": limit,
        }
        if genre:
            params["genres.name"] = genre
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            # Для отладки, вывести полный URL запроса
            print(f"Запрос к API: {response.url}")
            data = response.json()
            return data.get("docs", [])
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к API Кинопоиска: {e}")
            return []
