import sqlite3
from datetime import datetime
import logging

# Logging sozlamasi
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def log_sql(statement):
    """SQL so'rovlarini konsolda chiqarish uchun funksiya."""
    print(f"""
_____________________________________________________        
Executing: 
{statement}
_____________________________________________________
""")

class Database:
    def __init__(self, path_to_db="main.db"):
        self.path_to_db = path_to_db

    @property
    def connection(self):
        """Ma'lumotlar bazasiga ulanish."""
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        """SQL so'rovini bajarish."""
        if not parameters:
            parameters = ()
        connection = self.connection
        connection.set_trace_callback(log_sql)  # logger o'rniga log_sql ishlatiladi
        cursor = connection.cursor()
        data = None
        try:
            cursor.execute(sql, parameters)
            if commit:
                connection.commit()
            if fetchall:
                data = cursor.fetchall()
            if fetchone:
                data = cursor.fetchone()
        except sqlite3.Error as e:
            logger.error(f"SQLite error: {e}")
            connection.rollback()
            raise
        finally:
            connection.close()
        return data

    @staticmethod
    def format_args(sql, parameters: dict):
        """SQL so'rovi uchun parametrlarni formatlash."""
        sql += " AND ".join([f"{item} = ?" for item in parameters])
        return sql, tuple(parameters.values())