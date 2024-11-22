from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from states.states import Search, SearchName
from loader import dp,kino_db,user_db
from aiogram.dispatcher import FSMContext
import logging
from data.config import ADMINS



@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    try:
        telegram_id = message.from_user.id
        username = message.from_user.username

        if not user_db.select_user(telegram_id=telegram_id):
            user_db.add_user(telegram_id=telegram_id, username=username)
            logging.info(f"Foydalanuvchi qo'shildi telegram_id:{telegram_id} username: {username}")
            await message.answer("Siz yangi foydalanuvchisiz!")

            count = user_db.count_users()
            for admin in ADMINS:
                await dp.bot.send_message(
                    admin,
                    f"Telegram ID: {telegram_id}\n"
                    f"Username : {username}\n"
                    f"Toliq ismi :{message.from_user.full_name}\n"
                    f"Foydalanuvchi bazaga qo'shildi\n\n"
                    f"Bazada <b>{count[0]}</b>  ta foydalanuvchi bor"
                )
    except Exception as err:
        logging.exception(err)
    await message.answer(f"Salom, {message.from_user.full_name}!\n/kino - Kinoni olish uchun")

@dp.message_handler(commands='kino')
async def from_id(message:types.Message):
    await message.answer("Kodni yuboring")
    await Search.waiting.set()

@dp.message_handler(state=Search.waiting)
async def wait_for_post_id(message: types.Message, state: FSMContext):
    try:
        kino_kod = int(message.text)
    except ValueError:
        await message.reply("Siz kino kodi yubormadingiz.\nKino kodi raqamdan iborat.\nQayta qidirishga kirish uchun /start ni bosing")
        await state.finish()
        return
    kino = kino_db.get_movie_by_post_id(kino_kod)
    if kino:
        file_id = kino['file_id']
        caption=kino_db.get_movie_by_post_id(kino_kod)
        await message.answer_video(file_id,caption=kino['caption'],protect_content=True)
    else:
        await message.answer("Kino topilmadi.")
    await state.finish()

@dp.message_handler(commands='name')
async def from_name(message:types.Message):
    await message.answer("Kino nomini yuboring")
    await SearchName.waiting.set()

@dp.message_handler(state=SearchName.waiting)
async def from_name_wait(message:types.Message, state:FSMContext):
    kino_name=message.text
    kino=kino_db.get_movie_by_name(kino_name)
    if kino:
        vd=kino['file_id']
        capt=kino['caption']
        await message.answer_video(vd,caption=capt,protect_content=True)
    else:
        await message.answer("Kino topilmadi.")
    await state.finish()