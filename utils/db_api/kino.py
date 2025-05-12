from .database import Database
from datetime import datetime

# Kinolarni saqlash uchun KinoDatabase klassi
class KinoDatabase(Database):
    def create_table_kino(self):
        sql = """
                CREATE TABLE IF NOT EXISTS Kino(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id BIGINT NOT NULL UNIQUE,
                    file_id VARCHAR(2000) NOT NULL,
                    caption TEXT NULL,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    count_download INTEGER NOT NULL DEFAULT 0,
                    updated_at DATETIME
                );
              """
        self.execute(sql, commit=True)

    def add_kino(self, post_id: int, file_id: str, caption: str):
        # Bazada kino mavjudligini tekshirish
        existing_kino = self.search_kino_by_post_id(post_id)
        if existing_kino:
            raise ValueError("Bu kod bilan kino allaqachon mavjud.")

        sql = """
            INSERT INTO Kino(post_id, file_id, caption, created_at, updated_at)
            VALUES(?,?,?,?,?)
        """
        timestamp = datetime.now().isoformat()
        self.execute(sql, parameters=(post_id, file_id, caption, timestamp, timestamp), commit=True)

    def delete_kino(self, post_id: int):
        sql = "DELETE FROM Kino WHERE post_id=?"
        self.execute(sql, parameters=(post_id,), commit=True)

    def search_kino_by_post_id(self, post_id: int):
        sql = "SELECT file_id, caption, count_download FROM Kino WHERE post_id=?"
        result = self.execute(sql, parameters=(post_id,), fetchone=True)
        if result:
            return {"file_id": result[0], "caption": result[1], "count_download": result[2]}
        return None

    def count_kinos(self):
        sql = "SELECT COUNT(*) FROM Kino"
        result = self.execute(sql, fetchone=True)
        return {"Jami Kinolar": result[0] if result else 0}

    def search_kino_by_caption(self, caption: str):
        sql = "SELECT file_id, caption FROM Kino WHERE caption LIKE ?"
        return self.execute(sql, (f"%{caption}%",), fetchall=True)

    def update_download_count(self, post_id: int):
        sql = "UPDATE Kino SET count_download = count_download + 1 WHERE post_id = ?"
        self.execute(sql, parameters=(post_id,), commit=True)

    def get_download_count(self, post_id: int):
        sql = "SELECT count_download FROM Kino WHERE post_id = ?"
        result = self.execute(sql, parameters=(post_id,), fetchone=True)
        return result[0] if result else 0
