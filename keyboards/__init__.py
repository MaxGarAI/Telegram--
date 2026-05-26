# Экспортируем функцию создания главной клавиатуры,
# чтобы её можно было импортировать напрямую из пакета: `from keyboards import get_main_keyboard`
from .keyboards import get_main_keyboard
