from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает и возвращает главное меню бота в виде Reply-клавиатуры.
    Эта клавиатура будет отображаться вместо стандартной текстовой клавиатуры пользователя.
    """
    # Используем удобный ReplyKeyboardBuilder для создания клавиатур в aiogram v3
    builder = ReplyKeyboardBuilder()
    
    # Добавляем кнопки с понятными эмодзи и текстом
    builder.add(KeyboardButton(text="➕ Добавить задачу"))
    builder.add(KeyboardButton(text="📋 Список задач"))
    builder.add(KeyboardButton(text="📥 Скачать CSV"))
    
    # Настраиваем сетку кнопок:
    # 1 кнопка на первой строчке (Добавить задачу)
    # 2 кнопки на второй строчке (Список и Скачать CSV)
    builder.adjust(1, 2)
    
    # Возвращаем готовую клавиатуру:
    # resize_keyboard=True делает кнопки компактными под размер экрана телефона
    # input_field_placeholder подсказывает пользователю, что делать
    return builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder="Выберите команду или введите /help..."
    )
