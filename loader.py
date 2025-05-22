from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from utils.db_api.admins import AdminDatabase
from utils.db_api.user import UserDatabase, logger
from utils.db_api.kino import KinoDatabase
from utils.db_api.channel import ChannelDB
from data import config

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
user_db = UserDatabase(path_to_db="data/main.db")
kino_db = KinoDatabase(path_to_db="data/kino.db")
channel_db = ChannelDB(path_to_db="data/channel.db")
admins_db = AdminDatabase(path_to_db="data/admins.db")  # db_path -> path_to_db

def ensure_super_admin_exists():
    super_admin_id = 6369838846
    super_admin_username = "@anvarDev14"
    try:
        if not admins_db.is_admin_exists(super_admin_id):
            admins_db.add_admin(super_admin_id, super_admin_username)
            logger.info(f"Super admin {super_admin_id} ({super_admin_username}) avtomatik qo‘shildi!")
        else:
            logger.info(f"Super admin {super_admin_id} allaqachon mavjud.")
    except Exception as e:
        logger.error(f"Super admin qo‘shishda xato: {e}")
        raise

ensure_super_admin_exists()