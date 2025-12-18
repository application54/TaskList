# Модуль работы с базой данных

import sqlite3
import os
from src.security import SecurityManager
from src.config import DB_NAME

# Класс управления базой данных
class DatabaseManager:

    # Инициализация подключения к базе данных
    def __init__(self, db_path: str = DB_NAME):
        self.db_path = db_path
        self.security = SecurityManager()
        self._init_database()

    # Инициализация структуры базы данных
    def _init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                username TEXT,
                encrypted_password TEXT NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    # Добавление нового пароля
    def add_password(self, title: str, website: str, username: str,
                     password: str, notes: str, master_password: str) -> bool:
        try:
            encrypted_password = self.security.encrypt(password, master_password)
            if not encrypted_password:
                return False
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO passwords (title, username, encrypted_password, notes)
                VALUES (?, ?, ?, ?)
            ''', (title, username, encrypted_password, notes))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка добавления пароля: {e}")
            return False

    # Получение всех паролей
    def get_all_passwords(self, master_password: str):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM passwords ORDER BY title')
            rows = cursor.fetchall()
            passwords = []
            for row in rows:
                try:
                    decrypted_password = self.security.decrypt(row[3], master_password)
                    if decrypted_password:
                        passwords.append({
                            'id': row[0],
                            'title': row[1],
                            'username': row[2],
                            'password': decrypted_password,
                            'notes': row[4],
                            'created_at': row[5]
                        })
                except Exception as e:
                    print(f"Ошибка расшифровки пароля ID {row[0]}: {e}")
                    continue
            conn.close()
            return passwords
        except Exception as e:
            print(f"Ошибка получения паролей: {e}")
            return []

    # Удаление пароля
    def delete_password(self, password_id: int) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM passwords WHERE id = ?", (password_id,))
            conn.commit()
            conn.close()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Ошибка удаления пароля: {e}")
            return False