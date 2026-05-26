from aiogram import Router, html
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from keyboards import get_main_keyboard

# Создаем роутер для команд приветствия
router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    """
    Обработчик команды /start.
    Срабатывает, когда пользователь впервые запускает бота или вводит /start.
    Отправляет теплое приветствие и показывает меню с кнопками.
    """
    # Получаем полное имя пользователя (имя + фамилия, если указана)
    user_name = message.from_user.full_name
    
    # Формируем приветственный текст с использованием HTML разметки для красоты
    welcome_text = (
        f"👋 Привет, {html.bold(user_name)}!\n\n"
        f"🤖 Я командный <b>Task-бот</b> для совместной работы.\n"
        f"Помогаю всей вашей команде вести общий список задач прямо в Telegram!\n\n"
        f"📋 <b>Что я умею:</b>\n"
        f"• Добавлять задачи в общий пул команды.\n"
        f"• Выводить весь список задач в чат.\n"
        f"• Выгружать задачи в файл формата CSV для Excel.\n\n"
        f"💡 Используйте удобное меню кнопок внизу или отправьте /help для списка команд!"
    )
    
    # Отправляем сообщение и прикрепляем нашу клавиатуру из пакета keyboards
    await message.answer(
        text=welcome_text,
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

@router.message(Command("help"))
@router.message(lambda message: message.text == "❓ Помощь") # Также ловим кнопку помощь, если добавим
async def cmd_help(message: Message):
    """
    Обработчик команды /help.
    Выводит список всех доступных команд с кратким описанием.
    """
    help_text = (
        "📖 <b>Справочник команд бота:</b>\n\n"
        "➕ <b>Добавление задач:</b>\n"
        "• Наберите <code>/add [текст задачи]</code> — например: <code>/add Подготовить отчет за май</code>\n"
        "• Либо просто нажмите кнопку <b>➕ Добавить задачу</b> (я сам спрошу текст следующей строкой).\n\n"
        "📋 <b>Просмотр списка:</b>\n"
        "• Наберите <code>/list</code> или нажмите кнопку <b>📋 Список задач</b>.\n\n"
        "📥 <b>Экспорт данных:</b>\n"
        "• Наберите <code>/list_csv</code> или нажмите кнопку <b>📥 Скачать CSV</b>.\n\n"
        "ℹ️ <code>/help</code> — показать это справочное сообщение."
    )
    
    await message.answer(
        text=help_text,
        parse_mode="HTML"
    )
