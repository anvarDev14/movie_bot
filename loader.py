from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from utils.db_api.users import UserDatatbase
from utils.db_api.kino import KinoDatabase
from data import config

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
user_db=UserDatatbase(path_to_db="data/main.db")
kino_db=KinoDatabase(path_to_db="data/kino.db")

