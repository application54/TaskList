# Модуль работы с базой данных

import sqlite3
from datetime import datetime
from src.config import DB_NAME

# Класс управления базой данных
class DatabaseManager:

    # Инициализация подключения к базе данных
    def __init__(self, db_path: str = DB_NAME):
        self.db_path = db_path
        self._init_database()

    # Инициализация структуры базы данных
    def _init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority INTEGER DEFAULT 1,  -- 1: низкий, 2: средний, 3: высокий
                status INTEGER DEFAULT 0,    -- 0: не выполнено, 1: выполнено
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                deadline TIMESTAMP
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON tasks(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_priority ON tasks(priority)')
        conn.commit()
        conn.close()

    # Добавление новой задачи в базу данных
    def add_task(self, title: str, description: str = "", priority: int = 1, deadline: str = None) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tasks (title, description, priority, deadline)
                VALUES (?, ?, ?, ?)
            ''', (title, description, priority, deadline))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка добавления задачи: {e}")
            return False

    # Получение списка задач с возможностью фильтрации и поиска
    def get_all_tasks(self, filter_type: str = "all", search_term: str = ""):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            query = "SELECT * FROM tasks WHERE 1=1"
            params = []
            if filter_type == "active":
                query += " AND status = 0"
            elif filter_type == "completed":
                query += " AND status = 1"
            if search_term:
                query += " AND (title LIKE ? OR description LIKE ?)"
                params.extend([f"%{search_term}%", f"%{search_term}%"])
            query += " ORDER BY status ASC, priority DESC, created_at DESC"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            tasks = []
            for row in rows:
                tasks.append({
                    'id': row['id'],
                    'title': row['title'],
                    'description': row['description'] or '',
                    'priority': row['priority'],
                    'status': row['status'],
                    'created_at': row['created_at'],
                    'completed_at': row['completed_at'],
                    'deadline': row['deadline']
                })
            conn.close()
            return tasks
        except Exception as e:
            print(f"Ошибка получения задач: {e}")
            return []

    # Обновление статуса задачи
    def update_task_status(self, task_id: int, status: int) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            completed_at = datetime.now().isoformat() if status == 1 else None
            cursor.execute('''
                UPDATE tasks 
                SET status = ?, completed_at = ?
                WHERE id = ?
            ''', (status, completed_at, task_id))
            conn.commit()
            conn.close()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Ошибка обновления статуса задачи: {e}")
            return False

    # Обновление данных задачи
    def update_task(self, task_id: int, title: str, description: str, priority: int, deadline: str = None) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE tasks 
                SET title = ?, description = ?, priority = ?, deadline = ?
                WHERE id = ?
            ''', (title, description, priority, deadline, task_id))
            conn.commit()
            conn.close()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Ошибка обновления задачи: {e}")
            return False

    # Удаление конкретной задачи по ID
    def delete_task(self, task_id: int) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            conn.close()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Ошибка удаления задачи: {e}")
            return False

    # Удаление всех выполненных задач
    def delete_completed_tasks(self) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE status = 1")
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка удаления выполненных задач: {e}")
            return False

    # Получение статистики по задачам
    def get_statistics(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM tasks")
            total = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 1")
            completed = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 0")
            active = cursor.fetchone()[0]
            cursor.execute("""
                SELECT COUNT(*) FROM tasks 
                WHERE deadline IS NOT NULL 
                AND date(deadline) < date('now') 
                AND status = 0
            """)
            overdue = cursor.fetchone()[0]
            conn.close()
            return {
                'total': total,
                'completed': completed,
                'active': active,
                'overdue': overdue
            }
        except Exception as e:
            print(f"Ошибка получения статистики: {e}")
            return {'total': 0, 'completed': 0, 'active': 0, 'overdue': 0}