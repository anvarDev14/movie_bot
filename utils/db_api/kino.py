from datetime import datetime
from .database import Database

class KinoDatabase(Database):
    def create_table_kino(self):
        sql = """
            CREATE TABLE IF NOT EXISTS Kino(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER UNIQUE NOT NULL,
                file_id VARCHAR(3000) NOT NULL,
                caption TEXT NULL,
                name TEXT NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME
            );
        """
        self.execute(sql, commit=True)

    def add_movie(self, post_id: int, file_id: str, name: str, caption: str = None, created_at: str = None, updated_at: str = None):
        if self.get_movie_by_post_id(post_id):
            raise ValueError(f"post_id {post_id} allaqachon bazada mavjud.")

        sql = """
            INSERT INTO Kino (post_id, file_id, name, caption, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        timestamp = datetime.now().isoformat()
        created_at = created_at or timestamp
        updated_at = updated_at or timestamp
        self.execute(sql, parameters=(post_id, file_id, name, caption, created_at, updated_at), commit=True)

    def update_kino_caption(self, new_caption: str, post_id: int):
        sql = """
            UPDATE Kino
            SET caption = ?, updated_at = ?
            WHERE post_id = ?
        """
        updated_time = datetime.now().isoformat()
        self.execute(sql, parameters=(new_caption, updated_time, post_id), commit=True)

    def kinoni_codin_chiqarish(self,post_id:int):
        sql = "SELECT post_id FROM Kino"
        self.execute(sql, fetchall=True)


    def get_movie_by_post_id(self, post_id: int):
        sql = """
            SELECT file_id, caption FROM Kino
            WHERE post_id=?
        """
        result = self.execute(sql, parameters=(post_id,), fetchone=True)
        if result:
            return {
                'file_id': result[0],
                'caption': result[1]
            }
        return None

    def get_movie_by_name(self, name: str):
        sql = """
            SELECT file_id, caption FROM Kino
            WHERE name=?
        """
        result = self.execute(sql, parameters=(name,), fetchone=True)
        if result:
            return {
                'file_id': result[0],
                'caption': result[1]
            }
        return None

    def delete_movie(self, post_id: int):
        sql = """
            DELETE FROM Kino WHERE post_id = ?
        """
        self.execute(sql, parameters=(post_id,), commit=True)

    def count_kino(self):
        sql = """
            SELECT COUNT(*) FROM Kino
        """
        result = self.execute(sql, fetchone=True)
        return result[0] if result else 0

    def get_movies_bugun(self):
        sql = """
            SELECT name FROM Kino
            WHERE DATE(created_at) = DATE('now')
        """
        return self.execute(sql, fetchall=True)

    def get_movies_hafta(self):
        sql = """
            SELECT name FROM Kino
            WHERE DATE(created_at) >= DATE('now', '-7 days')
        """
        return self.execute(sql, fetchall=True)

    # def get_movies_oy(self):
    #     sql = """
    #         SELECT name FROM Kino
    #         WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')
    #     """
    #     return self.execute(sql, fetchall=True)


def get_movies_oy(self):
    try:
        # SQL so'rovi: Joriy oyda qo'shilgan kinolarni olish
        sql = """
            SELECT name FROM Kino
            WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')
        """

        # SQL so'rovini bajarish
        result = self.execute(sql, fetchall=True)

        # Natijani konsolga chiqarish (debug qilish uchun)
        print("Joriy oy kinolari:", result)

        return result
    except Exception as e:
        # Xatolikni qayta ishlash va xatolik haqida ma'lumot chiqarish
        print(f"Xatolik yuz berdi: {e}")
        return None
