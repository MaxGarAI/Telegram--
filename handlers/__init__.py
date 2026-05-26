from aiogram import Router

# Импортируем роутеры из наших модулей
from .start import router as start_router
from .tasks import router as tasks_router

# Создаем единый главный роутер для всего бота
main_router = Router()

# Подключаем дочерние роутеры
# Порядок включения важен: диспетчер проверяет обработчики по очереди.
main_router.include_router(start_router)
main_router.include_router(tasks_router)
