from . database import Database
from datetime import datetime
class UserDatatbase(Database):
    def create_table_users(self):
        sql="""
        CREATE TABLE IF NOT EXISTS Users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id BIGINT NOT NULL,
            username VARCHAR(225) NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_active DATETIME NULL
            );
            """
        self.execute(sql,commit=True)

    def add_user(self,telegram_id:int,username:str,created_at=None):
        sql="""
            INSERT INTO Users(telegram_id,username,created_at) VALUES(?,?,?)
            """

        if created_at is None:
            created_at=datetime.now().isoformat()
        self.execute(sql,parameters=(telegram_id,username,created_at),commit=True)
    def select_all_users(self):
        sql="""
            SELECT * FROM Users
            """
        self.execute(sql,fetchall=True)

    def select_user(self, **kwargs):
        # SQL_EXAMPLE = "SELECT * FROM Users where id=1 AND Name='John'"
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, kwargs)

        return self.execute(sql, parameters=parameters, fetchone=True)

    def count_users(self):
        sql="""
            SELECT COUNT(*) FROM Users
            """
        self.execute(sql,fetchall=True)

    def delete_users(self):
        self.execute("DELETE FROM Users WHERE TRUE",commit=True)

    def select_all_user_ids(self):
        sql = "SELECT telegram_id FROM Users"
        connection = self.connection
        cursor = connection.cursor()
        cursor.execute(sql)
        ids = [row[0] for row in cursor.fetchall()]
        connection.close()
        return ids


