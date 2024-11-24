from aiogram import types
from states.states import Search
from loader import dp, kino_db, user_db
from aiogram.dispatcher import FSMContext
import logging
from data.config import ADMINS


@dp.message_handler(commands=['start', 'help'])
async def welcome_message(message: types.Message):
    """
    Foydalanuvchi `start` yoki `help` komandalarini bosganda yoki birinchi marta yozganda,
    avtomatik salomlashish xabari yuboriladi.
    """
    telegram_id = message.from_user.id
    username = message.from_user.username

    if not user_db.select_user(telegram_id=telegram_id):
        user_db.add_user(telegram_id=telegram_id, username=username)
        logging.info(f"Yangi foydalanuvchi qo‘shildi: telegram_id={telegram_id}, username={username}")

        count = user_db.count_users()
        for admin in ADMINS:
            await dp.bot.send_message(
                admin,
                f"Yangi foydalanuvchi:\n"
                f"Telegram ID: {telegram_id}\n"
                f"Username: {username}\n"
                f"To‘liq ism: {message.from_user.full_name}\n\n"
                f"Bazada jami foydalanuvchilar soni: <b>{count[0]}</b>"
            )

    await message.answer(
        f"Assalomu alaykum, {message.from_user.full_name}! 👋\n\n"
        "Iltimos, qidirayotgan kinoning kodini yuboring:"
    )
    await Search.waiting.set()


@dp.message_handler(state=Search.waiting, content_types=types.ContentType.TEXT)
async def process_kino_kod(message: types.Message, state: FSMContext):
    """
    Kino kodini qayta ishlash va foydalanuvchiga kino ma'lumotlarini taqdim etish.
    """
    try:
        kino_kod = int(message.text)
    except ValueError:
        await message.reply(
            "❌ Iltimos, faqat son kiriting. Kod faqat raqamlardan iborat bo‘lishi kerak."
        )
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
            "https://t.me/PremyeraFilm_A"
        )


@dp.message_handler()
async def process_unexpected_messages(message: types.Message):
    """
    Foydalanuvchi kino kodi yuborishdan tashqari boshqa xabar yuborganda javob beradi.
    """
    await message.answer("❌ Iltimos, kinoni kodi raqam sifatida yuboring.")
