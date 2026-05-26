import sys
import asyncio
import logging

# Настраиваем кодировку консоли на UTF-8 для поддержки кириллицы на Windows
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Импортируем конфигурации, базу данных и обработчики из созданных модулей
from config import BOT_TOKEN
from database import init_db
from handlers import main_router

async def main() -> None:
    """
    Основная асинхронная функция запуска бота.
    """
    # 1. Инициализируем базу данных SQLite (создаем файл и таблицу, если их нет)
    init_db()

    # Проверка на случай отсутствия токена
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TELEGRAM_TOKEN_HERE":
        print("[X] ОШИБКА: Бот не может быть запущен без токена!")
        print("Пожалуйста, заполните файл .env и перезапустите скрипт.")
        return

    # 2. Инициализируем объект бота.
    # Задаем ParseMode.HTML по умолчанию, чтобы все сообщения могли содержать <b>, <i> и т.д.
    bot = Bot(
        token=BOT_TOKEN, 
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # 3. Инициализируем Диспетчер (Dispatcher).
    # Это главный координатор бота, который распределяет события (сообщения) по роутерам.
    dp = Dispatcher()

    # 4. Подключаем наш центральный роутер со всеми обработчиками
    dp.include_router(main_router)

    print("\n========================================================")
    print("[*] Бот успешно запущен и начал опрашивать сервера Telegram!")
    print("Откройте Telegram, найдите вашего бота и введите /start")
    print("Для остановки бота нажмите: Ctrl+C")
    print("========================================================\n")

    # 5. Запуск long polling (длинного опроса)
    # Бот будет бесконечно опрашивать Telegram в ожидании новых сообщений
    # Мы отключаем обработку старых сообщений (skip_updates=True не обязателен в v3 по умолчанию,
    # но start_polling сам очищает очередь при запуске, если настроено)
    try:
        # Предварительно удаляем вебхук с серверов Telegram на случай конфликта,
        # а также очищаем очередь старых необработанных сообщений (drop_pending_updates=True)
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        # Корректно закрываем сессию бота при выходе
        await bot.session.close()

if __name__ == "__main__":
    # Настраиваем подробное логирование, чтобы видеть в консоли всю активность бота
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        stream=sys.stdout
    )
    
    # Запускаем асинхронное приложение
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Бот остановлен администратором.")
