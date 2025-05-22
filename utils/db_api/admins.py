import sqlite3
from typing import List, Tuple

class AdminDatabase:
    def __init__(self, path_to_db: str):
        self.conn = sqlite3.connect(path_to_db)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self) -> None:
        """Admins jadvalini yaratadi."""
        sql = """
        CREATE TABLE IF NOT EXISTS Admins (
            telegram_id BIGINT PRIMARY KEY,
            username TEXT NOT NULL
        );
        """
        self.cursor.execute(sql)
        self.conn.commit()

    def is_admin_exists(self, telegram_id: int) -> bool:
        """Telegram ID bo‘yicha admin mavjudligini tekshiradi."""
        sql = "SELECT 1 FROM Admins WHERE telegram_id = ? LIMIT 1;"
        self.cursor.execute(sql, (telegram_id,))
        return bool(self.cursor.fetchone())

    def add_admin(self, telegram_id: int, username: str) -> None:
        """Yangi admin qo‘shadi."""
        sql = "INSERT OR IGNORE INTO Admins (telegram_id, username) VALUES (?, ?);"
        self.cursor.execute(sql, (telegram_id, username))
        self.conn.commit()

    def get_admin_type(self, telegram_id: int) -> str:
        """Admin turini qaytaradi (statik qiymat, chunki admin_type ustuni yo‘q)."""
        return "admin"

    def get_all_admins(self) -> List[Tuple[int, str]]:
        """Barcha adminlarni qaytaradi."""
        sql = "SELECT telegram_id, username FROM Admins;"
        self.cursor.execute(sql)
        return [(row[0], row[1], "admin") for row in self.cursor.fetchall()]

    def delete_admin(self, telegram_id: int) -> None:
        """Adminni o‘chiradi."""
        sql = "DELETE FROM Admins WHERE telegram_id = ?;"
        self.cursor.execute(sql, (telegram_id,))
        self.conn.commit()

    def close(self) -> None:
        """Ma'lumotlar bazasi ulanishini yopadi."""
        self.conn.close()