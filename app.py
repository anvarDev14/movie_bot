from aiogram import executor

from handlers.users.middleware import SubscriptionMiddleware
from loader import dp, user_db, kino_db, admins_db
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands

dp.middleware.setup(SubscriptionMiddleware())


async def on_startup(dispatcher):
    # Birlamchi komandalar (/star va /help)
    await set_default_commands(dispatcher)

    try:
        user_db.create_table_users()
        kino_db.create_table_kino()
        admins_db.create_table_admin()

    except Exception as err:
        print(err)

    # Bot ishga tushgani haqida adminga xabar berish
    await on_startup_notify(dispatcher)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
