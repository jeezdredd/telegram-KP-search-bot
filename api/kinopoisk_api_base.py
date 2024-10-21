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
