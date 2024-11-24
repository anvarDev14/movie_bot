from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from states.states import Search
from loader import dp, kino_db, user_db
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
            logging.info(f"Foydalanuvchi qo‘shildi: telegram_id:{telegram_id}, username: {username}")

            count = user_db.count_users()
            for admin in ADMINS:
                await dp.bot.send_message(
                    admin,
                    f"Yangi foydalanuvchi qo‘shildi:\n"
                    f"Telegram ID: {telegram_id}\n"
                    f"Username: {username}\n"
                    f"To‘liq ismi: {message.from_user.full_name}\n\n"
                    f"Bazada jami foydalanuvchilar soni: <b>{count[0]}</b>"
                )
    except Exception as err:
        logging.exception(err)

    await message.answer(
        f"Assalomu alaykum, {message.from_user.full_name}! 👋\n\n"
        f"Iltimos, siz qidirayotgan kinoning kodini kiriting:"
    )
    await Search.waiting.set()


@dp.message_handler(state=Search.waiting)
async def wait_for_kino_kod(message: types.Message, state: FSMContext):
    try:
        kino_kod = int(message.text)
    except ValueError:
        await message.reply(
            "❌ Iltimos, faqat son kiriting. Kod faqat raqamlardan iborat bo‘lishi kerak.\n"
            "Qayta qidirishga kirish uchun /start ni bosing."
        )
        await state.finish()
        return

    kino = kino_db.get_movie_by_post_id(kino_kod)
    if kino:
        file_id = kino['file_id']
        caption = kino['caption']
        await message.answer_video(
            file_id,
            caption=f"{caption}\n\n🎥 Kinoni kod bo‘yicha izlash uchun kodni kiriting.",
            protect_content=True
        )
    else:
        await message.answer(
            "❌ Afsuski, bu kod bo‘yicha kino topilmadi.\n\n"
            "🔗 Yana ko‘proq kinolarni qidirish uchun kanalimizga tashrif buyuring: "
            "[PremyeraFilm_A](https://t.me/PremyeraFilm_A)"
        )
    await state.finish()
