import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env, если он существует в корне проекта
load_dotenv()

# Получаем токен бота. Если его нет, выбросим понятную ошибку при запуске
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Имя или путь к файлу базы данных SQLite3
DB_PATH = os.getenv("DB_PATH", "tasks.db")

# Небольшая проверка: если токен не указан, предупреждаем разработчика сразу
if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TELEGRAM_TOKEN_HERE":
    print("[!] ВНИМАНИЕ: Переменная BOT_TOKEN не установлена или содержит дефолтное значение!")
    print("Пожалуйста, создайте файл .env (скопировав его из .env.example) и пропишите туда настоящий токен.")
    print("Например:")
    print("BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ")
    print("--------------------------------------------------------------------------------")
