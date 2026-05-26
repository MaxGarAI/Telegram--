import io
import csv
from datetime import datetime

from aiogram import Router, F, html
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, BufferedInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

# Импортируем функции для работы с базой данных
from database import add_task, get_all_tasks

# Создаем роутер для задач
router = Router()

# Определяем состояния (FSM - Finite State Machine) для пошагового ввода данных
class TaskStates(StatesGroup):
    # Состояние ожидания текста задачи от пользователя
    waiting_for_task_text = State()

def get_user_identifier(message: Message) -> str:
    """
    Вспомогательная функция для получения красивого имени пользователя.
    Например: "Иван Петров (@username)" или просто "Иван Петров" / "@username".
    """
    user = message.from_user
    name_parts = []
    
    if user.first_name:
        name_parts.append(user.first_name)
    if user.last_name:
        name_parts.append(user.last_name)
        
    full_name = " ".join(name_parts)
    
    if user.username:
        if full_name:
            return f"{full_name} (@{user.username})"
        return f"@{user.username}"
        
    return full_name if full_name else f"User_{user.id}"

# ==================== ДОБАВЛЕНИЕ ЗАДАЧИ ====================

@router.message(Command("add"))
async def cmd_add(message: Message, command: CommandObject, state: FSMContext):
    """
    Обработчик команды /add.
    Срабатывает при вводе: `/add Текст задачи`
    Или просто `/add` без аргументов.
    """
    # Сбрасываем любые предыдущие состояния FSM, если они были
    await state.clear()
    
    # Проверяем, передал ли пользователь аргументы после команды
    if command.args:
        # Убираем лишние пробелы по краям
        task_text = command.args.strip()
        
        # Получаем имя отправителя
        user_name = get_user_identifier(message)
        
        # Сохраняем в БД
        add_task(task_text, user_name)
        
        # Отправляем подтверждение
        await message.answer(
            f"✅ Задача успешно добавлена в общий список!\n\n"
            f"📝 <b>Текст:</b> {html.quote(task_text)}\n"
            f"👤 <b>Добавил:</b> {html.bold(user_name)}",
            parse_mode="HTML"
        )
    else:
        # Если аргументов нет, включаем режим ожидания текста задачи (FSM)
        await state.set_state(TaskStates.waiting_for_task_text)
        await message.answer(
            "📝 Вы не указали текст задачи вместе с командой.\n"
            "Пожалуйста, <b>напишите текст задачи в следующем сообщении</b>:",
            parse_mode="HTML"
        )

@router.message(F.text == "➕ Добавить задачу")
async def btn_add_task(message: Message, state: FSMContext):
    """
    Обработчик нажатия на кнопку "➕ Добавить задачу" на клавиатуре.
    Включает состояние FSM для ожидания текста задачи.
    """
    await state.clear()
    await state.set_state(TaskStates.waiting_for_task_text)
    await message.answer(
        "📝 Введите <b>текст задачи</b>, которую хотите добавить в общий список:",
        parse_mode="HTML"
    )

@router.message(TaskStates.waiting_for_task_text)
async def process_task_text_fsm(message: Message, state: FSMContext):
    """
    Этот обработчик срабатывает только тогда, когда бот находится в состоянии
    ожидания текста задачи (TaskStates.waiting_for_task_text).
    """
    task_text = message.text.strip() if message.text else ""
    
    if not task_text:
        await message.answer("⚠️ Текст задачи не может быть пустым. Пожалуйста, напишите что-нибудь:")
        return
        
    # Получаем имя отправителя
    user_name = get_user_identifier(message)
    
    # Сохраняем задачу в SQLite
    add_task(task_text, user_name)
    
    # Очищаем состояние FSM, чтобы бот вернулся в обычный режим
    await state.clear()
    
    await message.answer(
        f"✅ Задача успешно добавлена!\n\n"
        f"📝 <b>Текст:</b> {html.quote(task_text)}\n"
        f"👤 <b>Добавил:</b> {html.bold(user_name)}",
        parse_mode="HTML"
    )

# ==================== ПРОСМОТР СПИСКА ЗАДАЧ ====================

@router.message(Command("list"))
@router.message(F.text == "📋 Список задач")
async def cmd_list(message: Message, state: FSMContext):
    """
    Обработчик команды /list и кнопки "📋 Список задач".
    Выводит красивый пронумерованный список всех задач из БД.
    """
    # На всякий случай сбрасываем состояние ввода задачи
    await state.clear()
    
    # Получаем все задачи из базы
    tasks = get_all_tasks()
    
    if not tasks:
        await message.answer(
            "✨ <b>Список задач пуст!</b>\n"
            "Все запланированные дела сделаны. Отличная работа! 🎉\n"
            "Чтобы добавить новую задачу, используйте команду /add или кнопку меню.",
            parse_mode="HTML"
        )
        return
        
    # Строим красивый ответ
    response_lines = [f"📋 <b>Общий список задач команды ({len(tasks)}):</b>\n"]
    
    for idx, task in enumerate(tasks, 1):
        # Преобразуем TIMESTAMP строку в красивую дату, если это возможно
        # По умолчанию SQLite подставляет YYYY-MM-DD HH:MM:SS
        created_at_str = task['created_at']
        try:
            dt = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S")
            formatted_date = dt.strftime("%d.%m.%Y %H:%M")
        except ValueError:
            formatted_date = created_at_str
            
        response_lines.append(
            f"{idx}. 📝 <b>{html.quote(task['text'])}</b>\n"
            f"   👤 <i>Добавил: {html.quote(task['user'])}</i>\n"
            f"   📅 <i>Создано: {formatted_date}</i>\n"
        )
        
    # Объединяем строки в одно сообщение
    response_text = "\n".join(response_lines)
    await message.answer(response_text, parse_mode="HTML")

# ==================== СКАЧИВАНИЕ CSV ====================

@router.message(Command("list_csv"))
@router.message(F.text == "📥 Скачать CSV")
async def cmd_list_csv(message: Message, state: FSMContext):
    """
    Обработчик команды /list_csv и кнопки "📥 Скачать CSV".
    Формирует CSV-файл в оперативной памяти и отправляет его пользователю.
    """
    await state.clear()
    
    # Получаем задачи
    tasks = get_all_tasks()
    
    if not tasks:
        await message.answer(
            "⚠️ Нет задач для экспорта. Добавьте хотя бы одну задачу!",
            parse_mode="HTML"
        )
        return
        
    # Создаем виртуальный текстовый файл в оперативной памяти
    output = io.StringIO()
    
    # Важнейший штрих для Excel: записываем BOM (Byte Order Mark) в начало файла.
    # Без этого Excel не поймет, что файл в кодировке UTF-8, и вместо русских букв отобразит кракозябры.
    output.write('\ufeff')
    
    # Создаем CSV writer с разделителем точка с запятой (стандарт для Excel в русскоязычной локали)
    writer = csv.writer(output, delimiter=';', lineterminator='\n')
    
    # Пишем заголовки столбцов
    writer.writerow(['ID задачи', 'Текст задачи', 'Кто добавил', 'Дата и время добавления'])
    
    # Записываем каждую задачу в файл
    for task in tasks:
        writer.writerow([
            task['id'],
            task['text'],
            task['user'],
            task['created_at']
        ])
        
    # Превращаем содержимое StringIO в байтовую строку в кодировке UTF-8
    csv_bytes = output.getvalue().encode('utf-8')
    output.close()
    
    # Создаем файл-объект в aiogram для отправки пользователю напрямую из ОЗУ
    current_date = datetime.now().strftime("%Y-%m-%d_%H-%M")
    file_name = f"team_tasks_{current_date}.csv"
    
    document = BufferedInputFile(
        file=csv_bytes,
        filename=file_name
    )
    
    # Отправляем документ пользователю в чат
    await message.answer_document(
        document=document,
        caption=f"📊 <b>Экспорт завершен!</b>\nВсего выгружено задач: {len(tasks)}\n"
                f"Файл отлично открывается в Excel.",
        parse_mode="HTML"
    )
