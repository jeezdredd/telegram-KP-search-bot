# api/booking_api.py
import requests


# Функция для запроса отелей через RapidAPI
def get_hotels_by_price(city, checkin_date, checkout_date, adults_number=1):
    url = "https://booking-com.p.rapidapi.com/v1/hotels/search"

    querystring = {
        "location_id": city,  # Здесь нужно указать ID города (его нужно будет найти через другой API запрос)
        "checkin_date": checkin_date,
        "checkout_date": checkout_date,
        "adults_number": adults_number,
        "order_by": "price",  # Сортировка по цене
        "units": "metric",
        "room_number": "1",
        "locale": "en-gb",
    }

    headers = {
        "X-RapidAPI-Key": "2891c2e49cmsh58275baacfc03dap10f681jsn6a647601a517",  # ключ от RapidAPI
        "X-RapidAPI-Host": "booking-com.p.rapidapi.com",
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        return response.json()
    else:
        return None
