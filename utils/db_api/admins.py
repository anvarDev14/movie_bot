from datetime import datetime
from .database import Database
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram import Bot



class AdminDatabase(Database):
    def create_table_admins(self):
        sql = """
            CREATE TABLE IF NOT EXISTS Admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id BIGINT UNIQUE NOT NULL,
                full_name VARCHAR(255) NOT NULL
            );
        """
        self.execute(sql, commit=True)


    def add_admin(self, telegram_id: int, full_name: str):
        sql = "INSERT INTO Admins (telegram_id, full_name) VALUES (?, ?);"
        self.execute(sql, parameters=(telegram_id, full_name), commit=True)

    def get_all_admins(self):
        sql = "SELECT telegram_id, full_name FROM Admins;"
        return self.execute(sql, fetchall=True)

    def delete_admin(self, telegram_id: int):
        sql = "DELETE FROM Admins WHERE telegram_id = ?;"
        self.execute(sql, parameters=(telegram_id,), commit=True)

    def is_admin(self, telegram_id: int):
        sql = "SELECT 1 FROM Admins WHERE telegram_id = ? LIMIT 1;"
        return bool(self.execute(sql, parameters=(telegram_id,), fetchone=True))

    def get_admin_ids(self):
        sql = "SELECT telegram_id FROM Admins"
        result = self.execute(sql, fetchall=True)
        return [row[0] for row in result] if result else []

    def is_admin_exists(self, telegram_id: int):
        """Berilgan telegram_id bo‘yicha admin mavjudligini tekshiradi"""
        sql = "SELECT COUNT(*) FROM Admins WHERE telegram_id = ?"
        result = self.execute(sql, (telegram_id,), fetchone=True)

        return result[0] > 0 if result else False

    def get_statistics(self):
        """Adminlar va foydalanuvchilar sonini olish"""
        sql_admins = "SELECT COUNT(*) FROM Admins;"
        sql_users = "SELECT COUNT(*) FROM Student;"

        admin_count = self.execute(sql_admins, fetchone=True)[0]
        user_count = self.execute(sql_users, fetchone=True)[0]

        return {"admins": admin_count, "users": user_count}



