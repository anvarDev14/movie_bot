from .database import Database
from datetime import datetime, timedelta
import pytz  # Mahalliy vaqt uchun kutubxona
import logging

# Logging sozlamasi
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UserDatabase(Database):
    def __init__(self, path_to_db: str):
        super().__init__(path_to_db)  # Ota sinfning konstruktorini chaqirish
        self.uzbekistan_tz = pytz.timezone("Asia/Tashkent")  # Mahalliy vaqt zonasini aniqlash

    def _get_current_time(self):
        """Joriy vaqtni olish uchun yordamchi funksiya."""
        return datetime.now(self.uzbekistan_tz)

    def _get_start_of_day(self, date: datetime):
        """Kun boshlanishini olish uchun yordamchi funksiya."""
        return date.replace(hour=0, minute=0, second=0, microsecond=0)

    def create_table_users(self):
        """Users jadvalini yaratish."""
        sql = """
            CREATE TABLE IF NOT EXISTS Users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id BIGINT NOT NULL,
                username VARCHAR(255) NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_active DATETIME NULL,
                is_admin BOOLEAN NOT NULL DEFAULT 0
            );
        """
        try:
            self.execute(sql, commit=True)
            logger.info("Users table created successfully.")
        except Exception as e:
            logger.error(f"Error creating Users table: {e}")
            raise

    def add_user(self, telegram_id: int, username: str):
        """Yangi foydalanuvchi qo'shish."""
        try:
            created_at = self._get_current_time().isoformat()  # Mahalliy vaqt
            sql = """
                INSERT INTO Users(telegram_id, username, created_at) VALUES(?, ?, ?)
            """
            logger.info(f"Attempting to add user: telegram_id={telegram_id}, username={username}, created_at={created_at}")
            self.execute(sql, parameters=(telegram_id, username, created_at), commit=True)
            logger.info(f"User {telegram_id} successfully added.")
        except Exception as e:
            logger.error(f"Failed to add user {telegram_id}: {e}")
            raise

    def select_all_users(self):
        """Barcha foydalanuvchilarni tanlash."""
        sql = """
            SELECT * FROM Users
        """
        return self.execute(sql, fetchall=True)

    def count_users(self):
        """Jami foydalanuvchilar sonini hisoblash."""
        sql = """
            SELECT COUNT(*) FROM Users
        """
        return self.execute(sql, fetchone=True)[0]

    def select_user(self, telegram_id: int):
        """Muayyan foydalanuvchini tanlash."""
        sql = """
            SELECT * FROM Users WHERE telegram_id = ?
        """
        return self.execute(sql, parameters=(telegram_id,), fetchone=True)

    def count_daily_users(self):
        """Kunlik yangi foydalanuvchilar sonini hisoblash."""
        now = self._get_current_time()
        today_start = self._get_start_of_day(now)
        tomorrow_start = today_start + timedelta(days=1)

        sql = """
            SELECT COUNT(*) FROM Users
            WHERE created_at >= ? AND created_at < ?
        """
        return self.execute(
            sql, parameters=(today_start.isoformat(), tomorrow_start.isoformat()), fetchone=True
        )[0]

    def count_weekly_users(self):
        """Haftalik yangi foydalanuvchilar sonini hisoblash."""
        now = self._get_current_time()
        one_week_ago = now - timedelta(days=7)

        sql = """
            SELECT COUNT(*) FROM Users
            WHERE created_at >= ?
        """
        return self.execute(sql, parameters=(one_week_ago.isoformat(),), fetchone=True)[0]

    def count_monthly_users(self):
        """Oylik yangi foydalanuvchilar sonini hisoblash."""
        now = self._get_current_time()
        one_month_ago = now - timedelta(days=30)

        sql = """
            SELECT COUNT(*) FROM Users
            WHERE created_at >= ?
        """
        return self.execute(sql, parameters=(one_month_ago.isoformat(),), fetchone=True)[0]

    def update_last_active(self, telegram_id: int):
        """Foydalanuvchining oxirgi faol vaqtini yangilash."""
        try:
            last_active = self._get_current_time().isoformat()  # Mahalliy vaqt
            sql = """
                UPDATE Users
                SET last_active = ?
                WHERE telegram_id = ?
            """
            self.execute(sql, parameters=(last_active, telegram_id), commit=True)
            logger.info(f"Last active updated for user {telegram_id}: {last_active}")
        except Exception as e:
            logger.error(f"Failed to update last_active for user {telegram_id}: {e}")
            raise

    def count_active_daily_users(self):
        """Kunlik faol foydalanuvchilar sonini hisoblash."""
        now = self._get_current_time()
        today_start = self._get_start_of_day(now)
        tomorrow_start = today_start + timedelta(days=1)

        sql = """
            SELECT COUNT(*) FROM Users
            WHERE last_active >= ? AND last_active < ?
        """
        return self.execute(
            sql, parameters=(today_start.isoformat(), tomorrow_start.isoformat()), fetchone=True
        )[0]

    def count_active_weekly_users(self):
        """Haftalik faol foydalanuvchilar sonini hisoblash."""
        now = self._get_current_time()
        one_week_ago = now - timedelta(days=7)

        sql = """
            SELECT COUNT(*) FROM Users
            WHERE last_active >= ?
        """
        return self.execute(sql, parameters=(one_week_ago.isoformat(),), fetchone=True)[0]

    def count_active_monthly_users(self):
        """Oylik faol foydalanuvchilar sonini hisoblash."""
        now = self._get_current_time()
        one_month_ago = now - timedelta(days=30)

        sql = """
            SELECT COUNT(*) FROM Users
            WHERE last_active >= ?
        """
        return self.execute(sql, parameters=(one_month_ago.isoformat(),), fetchone=True)[0]

    def check_if_admin(self, user_id: int):
        """Foydalanuvchining admin ekanligini tekshirish."""
        query = "SELECT is_admin FROM Users WHERE telegram_id = ?"
        result = self.execute(query, parameters=(user_id,), fetchone=True)
        return bool(result) and result[0] == 1

    def add_is_admin_column(self):
        """Jadvalga is_admin ustunini qo'shish."""
        try:
            sql = """
                ALTER TABLE Users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT 0
            """
            self.execute(sql, commit=True)
            logger.info("is_admin column added successfully.")
        except Exception as e:
            logger.warning(f"is_admin column might already exist: {e}")