# Telegram Hotel Search Bot

Этот проект представляет собой Telegram-бота для поиска отелей через API Booking.com. Бот взаимодействует с пользователями и предоставляет информацию о доступных отелях на основе их запросов.

## Описание

Telegram-бот может выполнять следующие функции:

- **/lowprice**: отображение самых дешёвых отелей в указанном городе.
- **/guest_rating**: предоставление информации о самых популярных отелях.
- **/bestdeal**: поиск отелей, которые находятся ближе всего к центру города.
- **/history**: просмотр истории запросов о поиске отелей.

## Установка

1. Клонируйте репозиторий:

   ```bash
   git clone https://your-repo-url
   ```

2. Перейти в директорию с репозиторием:

   ```bash
   cd telegram-hotel-search-bot
   ```
   
3. Установите зависимости:

   ```bash
   pip install -r requirements.txt
   ```
      
4. Создайте файл `.env` и добавьте в него переменные окружения:
    
    ```bash
    BOT_TOKEN=YOUR_BOT_TOKEN
   RAPID_API_KEY=YOUR_BOOKING_API_KEY
      ``` 
         
5. Запустите бота:
         
    ```bash
    python main.py
    ```
   