import sqlite3

class ChannelDB:
    def __init__(self, path_to_db):
        self.path_to_db = path_to_db
        self.conn = sqlite3.connect(path_to_db, check_same_thread=False)  # Multi-threading uchun
        self.cursor = self.conn.cursor()
        self.create_table()
        self.channels = self.load_channels()  # Jadvaldagi kanallarni yuklab olish

    def create_table(self):
        """Kanallar jadvalini yaratish"""
        self.cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS channels (
                channel_id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                static_link TEXT NOT NULL DEFAULT ''
            )
        ''')
        self.conn.commit()

    def load_channels(self):
        """Jadvaldagi kanallarni yuklab olish"""
        self.cursor.execute("SELECT channel_id, title, static_link FROM channels")
        return {channel_id: (title, static_link) for channel_id, title, static_link in self.cursor.fetchall()}

    def add_channel(self, channel_id, title, static_link):
        """Yangi kanalni jadvalga qo‘shish"""
        if not self.channel_exists(channel_id):  # Agar kanal mavjud bo‘lmasa
            self.cursor.execute("INSERT INTO channels (channel_id, title, static_link) VALUES (?, ?, ?)",
                                (channel_id, title, static_link))
            self.conn.commit()
            self.channels[channel_id] = (title, static_link)
            return True
        return False

    def channel_exists(self, channel_id):
        """Kanal mavjudligini tekshirish"""
        self.cursor.execute("SELECT 1 FROM channels WHERE channel_id = ?", (channel_id,))
        return bool(self.cursor.fetchone())

    def get_channel_link(self, channel_id):
        """Kanal havolasini olish"""
        self.cursor.execute("SELECT static_link FROM channels WHERE channel_id = ?", (channel_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_all_channels(self):
        """Barcha kanallarni olish"""
        self.cursor.execute("SELECT channel_id, title, static_link FROM channels")
        return self.cursor.fetchall()

    def delete_channel(self, channel_id):
        """Kanalni o‘chirish"""
        if self.channel_exists(channel_id):
            self.cursor.execute("DELETE FROM channels WHERE channel_id = ?", (channel_id,))
            self.conn.commit()
            if channel_id in self.channels:
                del self.channels[channel_id]
            return True
        return False

    def close(self):
        """Ma'lumotlar bazasi ulanishini yopish"""
        self.conn.close()