# models.py

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Movie:
    title: str
    description: str
    rating: Optional[float]
    year: Optional[int]
    genres: List[str]
    age_rating: Optional[int]
    poster_url: Optional[str]

    @classmethod
    def from_api_data(cls, data):
        title = data.get("name") or data.get("alternativeName") or "Без названия"
        description = data.get("description") or "Описание отсутствует."
        rating = data.get("rating", {}).get("kp") or data.get("rating", {}).get("imdb")
        year = data.get("year") or "Неизвестно"
        genres = [
            genre.get("name") for genre in data.get("genres", []) if genre.get("name")
        ]
        age_rating = data.get("ageRating")
        poster_url = data.get("poster", {}).get("url")
        return cls(title, description, rating, year, genres, age_rating, poster_url)
