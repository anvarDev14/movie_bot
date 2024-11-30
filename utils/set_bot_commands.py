from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Botni ishga tushurish, Kino qidirish"),
            types.BotCommand("help", "Yordam"),
            types.BotCommand("admin","Admin uchun menyu"),
            types.BotCommand("add_movie","Kino qo'shish"),
            types.BotCommand("delete_movie","Kinoni o'chirish"),
            types.BotCommand("update","captionni yangilash")
        ]
    )
