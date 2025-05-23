from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.handler import SkipHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.dispatcher.filters import Command
from data.config import ADMINS
from handlers.users.middleware import SubscriptionMiddleware
from handlers.users.reklama import ReklamaTuriState
from handlers.users.start import is_subscribed_to_all_channels, get_unsubscribed_channels, get_subscription_keyboard
from keyboards.inline.kino_button import orqa_inline
from loader import dp, bot, kino_db, user_db, channel_db
from keyboards.default.button_kino import menu_movie
from keyboards.default.admin_menu import admin_menu
import asyncio

# Middleware ni sozlash
def setup_subscription_middleware():
    dp.middleware.setup(SubscriptionMiddleware())

# Admin paneli
@dp.message_handler(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id in ADMINS:
        await message.answer("Admin paneliga xush kelibsiz! Kerakli bo‘limni tanlang:", reply_markup=admin_menu)
    else:
        await message.answer("Siz admin emassiz.")

class KinoAdd(StatesGroup):
    kino_add = State()
    kino_code = State()

class KinoDelete(StatesGroup):
    kino_code = State()
    is_confirm = State()

# Statistika ko‘rish
@dp.message_handler(text="📊 Statistika")
async def show_stats(message: types.Message):
    if message.from_user.id not in ADMINS:
        await message.answer("🚫 <b>Siz admin emassiz.</b>", parse_mode="HTML")
        return

    try:
        total_kinos = kino_db.count_kinos()
        total_users = user_db.count_users()
        daily_users = user_db.count_daily_users()
        weekly_users = user_db.count_weekly_users()
        monthly_users = user_db.count_monthly_users()
        active_daily = user_db.count_active_daily_users()
        active_weekly = user_db.count_active_weekly_users()
        active_monthly = user_db.count_active_monthly_users()

        stats_message = (
            "📊 <b>Statistika</b>\n"
            "─────────────────\n"
            "🎬 Kinolar: <b>{total_kinos}</b>\n"
            "👥 Foydalanuvchilar: <b>{total_users}</b>\n"
            "─────────────────\n"
            "🗓 Kunlik: <b>{daily_users}</b> | Faol: <b>{active_daily}</b>\n"
            "📅 Haftalik: <b>{weekly_users}</b> | Faol: <b>{active_weekly}</b>\n"
            "📆 Oylik: <b>{monthly_users}</b> | Faol: <b>{active_monthly}</b>"
        ).format(
            total_kinos=total_kinos,
            total_users=total_users,
            daily_users=daily_users,
            weekly_users=weekly_users,
            monthly_users=monthly_users,
            active_daily=active_daily,
            active_weekly=active_weekly,
            active_monthly=active_monthly
        )

        markup = InlineKeyboardMarkup().add(
            InlineKeyboardButton("🔄 Yangilash", callback_data="refresh_stats")
        )
        await message.answer(stats_message, parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        await message.answer("❌ <b>Statistika olishda xatolik yuz berdi.</b>", parse_mode="HTML")
        print(f"[Xatolik]: {e}")

# Callback handler - Yangilash tugmasi uchun
@dp.callback_query_handler(lambda c: c.data == "refresh_stats")
async def refresh_stats_callback(callback: types.CallbackQuery):
    stages = [
        "✨ <b>Yangilanmoqda</b> |◦◦◦◦◦|",
        "✨ <b>Yangilanmoqda</b> |●◦◦◦◦|",
        "✨ <b>Yangilanmoqda</b> |●●◦◦◦|",
        "✨ <b>Yangilanmoqda</b> |●●●◦◦|",
        "✨ <b>Yangilanmoqda</b> |●●●●◦|"
    ]

    for stage in stages:
        await callback.message.edit_text(stage, parse_mode="HTML")
        await asyncio.sleep(0.5)

    try:
        total_kinos = kino_db.count_kinos()
        total_users = user_db.count_users()
        daily_users = user_db.count_daily_users()
        weekly_users = user_db.count_weekly_users()
        monthly_users = user_db.count_monthly_users()
        active_daily = user_db.count_active_daily_users()
        active_weekly = user_db.count_active_weekly_users()
        active_monthly = user_db.count_active_monthly_users()

        stats_message = (
            "📊 <b>Statistika</b>\n"
            "─────────────────\n"
            "🎬 Kinolar: <b>{total_kinos}</b>\n"
            "👥 Foydalanuvchilar: <b>{total_users}</b>\n"
            "─────────────────\n"
            "🗓 Kunlik: <b>{daily_users}</b> | Faol: <b>{active_daily}</b>\n"
            "📅 Haftalik: <b>{weekly_users}</b> | Faol: <b>{active_weekly}</b>\n"
            "📆 Oylik: <b>{monthly_users}</b> | Faol: <b>{active_monthly}</b>"
        ).format(
            total_kinos=total_kinos,
            total_users=total_users,
            daily_users=daily_users,
            weekly_users=weekly_users,
            monthly_users=monthly_users,
            active_daily=active_daily,
            active_weekly=active_weekly,
            active_monthly=active_monthly
        )

        markup = InlineKeyboardMarkup().add(
            InlineKeyboardButton("🔄 Yangilash", callback_data="refresh_stats")
        )

        await callback.message.edit_text(stats_message, parse_mode="HTML", reply_markup=markup)
        await callback.answer("✅ Muvaffaqiyatli yangilandi!", show_alert=False)
    except Exception as e:
        error_message = (
            "❌ <b>Xatolik!</b>\n"
            " Ma'lumotlarni yangilab bo‘lmadi.\n"
            " Qayta urinib ko‘ring!"
        )
        await callback.message.edit_text(
            error_message,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("♻️ Qayta urinish", callback_data="refresh_stats")
            )
        )
        print(f"[Xatolik]: {e}")
        await callback.answer("❌ Xatolik yuz berdi!", show_alert=False)

# Kino qo‘shish
@dp.message_handler(text=" ➕ Kino Qo‘shish")
async def message_kino_add(message: types.Message, state: FSMContext):
    admin_id = message.from_user.id
    if admin_id in ADMINS:
        await KinoAdd.kino_add.set()
        await message.answer("Kinoni yuboring")
    else:
        await message.answer("Siz admin emassiz")

@dp.message_handler(text="🔙 Admin menyu", state=KinoAdd.kino_add)
async def cancel_kino_add(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Jarayon bekor qilindi. Siz bosh menyudasiz.", reply_markup=admin_menu)

@dp.message_handler(state=KinoAdd.kino_add, content_types=types.ContentType.VIDEO)
async def kino_file_handler(message: types.Message, state: FSMContext):
    if message.video is None:
        await message.answer("❌ Video faylni yuborish kerak.")
        return

    async with state.proxy() as data:
        data['file_id'] = message.video.file_id
        data['caption'] = message.caption

    await KinoAdd.kino_code.set()
    await message.answer("📎 <b>Kino uchun Kod kiriting:</b>", parse_mode='HTML')

@dp.message_handler(state=KinoAdd.kino_code, content_types=types.ContentType.TEXT)
async def kino_code_handler(message: types.Message, state: FSMContext):
    try:
        post_id = int(message.text)
        existing_kino = kino_db.search_kino_by_post_id(post_id)
        if existing_kino:
            await message.answer("⚠️ Bu kod bilan kino allaqachon mavjud. Iltimos, boshqa kod kiriting.")
            return

        async with state.proxy() as data:
            data['post_id'] = post_id
            kino_db.add_kino(post_id=data['post_id'], file_id=data['file_id'], caption=data['caption'])

        await message.answer("✅ Kino muvaffaqiyatli qo‘shildi.")
        await state.finish()
    except ValueError:
        await message.answer("❌ Iltimos kino kodni faqat raqam bilan yuboring.")

# Kino o‘chirish
@dp.message_handler(text="🗑 Kino O‘chirish")
async def movie_delete_handler(message: types.Message):
    admin_id = message.from_user.id
    if admin_id in ADMINS:
        await KinoDelete.kino_code.set()
        await message.answer("🗑 O'chirmoqchi bo'lgan kino kodini yuboring")
    else:
        await message.answer("🚫 Siz admin emassiz")

@dp.message_handler(state=KinoDelete.kino_code, content_types=types.ContentType.TEXT)
async def movie_kino_code(message: types.Message, state: FSMContext):
    if message.text == "🔙 Admin menyu":
        await state.finish()
        await message.answer("Jarayon bekor qilindi. Siz bosh menyudasiz.", reply_markup=admin_menu)
        return

    if not message.text.isdigit():
        await message.answer("❌ Iltimos, kino kodini faqat raqam shaklida kiriting.")
        return

    async with state.proxy() as data:
        data['post_id'] = int(message.text)
        result = kino_db.search_kino_by_post_id(data['post_id'])

        if result:
            await message.answer_video(video=result['file_id'], caption=result['caption'])
            await KinoDelete.is_confirm.set()
            await message.answer("Quyidagilardan birini tanlang", reply_markup=menu_movie)
        else:
            await message.answer(f"⚠️ <b>{data['post_id']}</b> kod bilan kino topilmadi.", parse_mode="HTML")

@dp.message_handler(state=KinoDelete.is_confirm, content_types=types.ContentType.TEXT)
async def movie_kino_delete(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['is_confirm'] = message.text
        if data['is_confirm'] == "✅Tasdiqlash":
            kino_db.delete_kino(data['post_id'])
            await message.answer("Kino muvaffaqiyatli o'chirildi", reply_markup=ReplyKeyboardRemove())
            await state.finish()
        elif data['is_confirm'] == "❌Bekor qilish":
            await message.answer("Bekor qilindi", reply_markup=ReplyKeyboardRemove())
            await state.finish()
        else:
            await message.answer("Iltimos quyidagi tugmalardan birini tanlang", reply_markup=menu_movie)

# Kino qidirish (foydalanuvchi tarafi)
@dp.message_handler(lambda x: x.text.isdigit())
async def search_kino_handler(message: types.Message):
    user_id = message.from_user.id
    user_db.update_last_active(user_id)
    post_id = int(message.text)
    data = kino_db.search_kino_by_post_id(post_id)
    if data:
        try:
            await bot.send_video(
                chat_id=user_id,
                video=data['file_id'],
                caption=(
                    f"{data['caption']}\n\n"
                    f"📥 Kino Yuklash Soni: {data['count_download']}\n\n"
                    f"📌 Barcha kinolar: https://t.me/premiermoviekanal kanalda\n\n"
                )
            )
            kino_db.update_download_count(post_id)
        except Exception as err:
            await message.answer(f"❌ Kino yuborishda xatolik: {err}")
    else:
        await message.answer(f"⚠️ {post_id} kodi bilan kino topilmadi.")

# Bosh menyuga qaytish
@dp.message_handler(text="🔙 Admin menyu", state=[ReklamaTuriState.tur, KinoDelete.kino_code, KinoAdd.kino_code])
async def back_to_main_menu(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Jarayon Bekor Bo'ldi Admin Menyudasiz.", reply_markup=admin_menu)

# Bekor qilish handleri
@dp.message_handler(
    lambda message: message.text in ["➕ Kino Qo‘shish", "📊 Statistika", "📣 Reklama", "🗑 Kino O‘chirish"], state="*")
@dp.message_handler(lambda message: message.text.lower() in ["bekor qilish", "/cancel"], state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()
    if message.from_user.id in ADMINS:
        await message.answer("Jarayon bekor qilindi. Siz Admin menyudasiz.", reply_markup=admin_menu)
    else:
        await message.answer("Jarayon bekor qilindi.", reply_markup=ReplyKeyboardRemove())

# Middleware ni faollashtirish
setup_subscription_middleware()