# utils/notify_admins.py
import logging
from aiogram import Dispatcher
from data.config import ADMINS

async def on_startup_notify(dp: Dispatcher):
    for admin in ADMINS:
        try:
            await dp.bot.send_message(admin, "Bot ishga tushdi 🎉")
        except Exception as e:
            logging.error(f"Admin {admin} ga xabar yuborishda xatolik: {e}")