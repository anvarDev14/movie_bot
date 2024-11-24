from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from loader import dp, kino_db, user_db
import logging
from data.config import ADMINS


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    """
    Foydalanuvchi botga birinchi marta kirganda, bot avtomatik kino kodi so‘raydi.
    """
    telegram_id = message.from_user.id
    username = message.from_user.username

    # Foydalanuvchini bazaga qo'shish
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

    # Foydalanuvchi birinchi marta startni bosganida kino kodi so‘raladi
    await message.answer(
        f"Assalomu alaykum, {message.from_user.full_name}! 👋\n\n"
        "Iltimos, qidirayotgan kinoning kodini yuboring. Kod faqat raqamlardan iborat bo‘lishi kerak."
    )


@dp.message_handler(content_types=types.ContentType.TEXT)
async def process_kino_kod(message: types.Message, state: FSMContext):
    """
    Kino kodini qayta ishlash va foydalanuvchiga kino ma'lumotlarini taqdim etish.
    """
    try:
        kino_kod = int(message.text)
    except ValueError:
        await message.reply(
            "❌ Iltimos, faqat son kiriting. Kino kodi raqamdan iborat bo‘lishi kerak."
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
