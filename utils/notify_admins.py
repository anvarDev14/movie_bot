# notify_admins.py
import logging
from aiogram import Dispatcher
from aiogram.utils.exceptions import ChatNotFound, BotBlocked

async def on_startup_notify(dp: Dispatcher):
    from data import config  # ADMINS ro'yxatini configdan olish
    for admin in config.ADMINS:
        try:
            await dp.bot.send_message(admin, "Bot ishga tushdi")
        except ChatNotFound:
            logging.error(f"Chat not found for admin ID: {admin}")
        except BotBlocked:
            logging.error(f"Bot blocked by admin ID: {admin}")
        except Exception as e:
            logging.error(f"Error sending message to admin ID {admin}: {e}")