import sqlite3
from config import DB_PATH

def init_db():
    """
    Инициализирует базу данных SQLite.
    Создает таблицу 'tasks', если её еще нет в файле БД.
    Это вызывается один раз при старте бота в main.py.
    """
    # Устанавливаем соединение с файлом базы данных
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Создаем таблицу согласно требованиям к полям:
    # id - уникальный номер (автоинкремент)
    # text - текст задачи
    # user - имя пользователя (кто добавил)
    # created_at - дата и время создания задачи (подставляется автоматически)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            user TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()
    print("[БД] База данных SQLite успешно инициализирована.")

def add_task(text: str, user: str) -> None:
    """
    Добавляет новую задачу в таблицу tasks.
    :param text: Текст задачи.
    :param user: Имя или никнейм пользователя, добавившего задачу.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Используем безопасные плейсхолдеры (?) для защиты от SQL-инъекций
    cursor.execute(
        "INSERT INTO tasks (text, user) VALUES (?, ?)", 
        (text, user)
    )
    
    conn.commit()
    conn.close()

def get_all_tasks():
    """
    Возвращает список всех задач из базы данных.
    Каждая задача представлена в виде объекта sqlite3.Row,
    который ведет себя как словарь (можно обращаться по ключам: task['text']).
    """
    conn = sqlite3.connect(DB_PATH)
    
    # Настраиваем row_factory, чтобы строки возвращались с доступом по именам колонок
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Получаем все задачи, сортируя их по дате создания от старых к новым
    cursor.execute("SELECT id, text, user, created_at FROM tasks ORDER BY created_at ASC")
    tasks = cursor.fetchall()
    
    conn.close()
    return tasks
