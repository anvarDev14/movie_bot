import logging
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from handlers.users.kino_handler import setup_subscription_middleware
from keyboards.default.admin_menu import admin_menu, admin_menu1
from loader import dp, admins_db
from data.config import SUPER_ADMINS

# Logging sozlamalari
logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Yangi holatlar
class AdminStates(StatesGroup):
    admin = State()
    super_admin = State()
    movie = State()
    delete_movie = State()

# Umumiy foydalanuvchi ma'lumotlari
def get_user_info(message: types.Message) -> tuple[int, str]:
    return message.from_user.id, message.from_user.username or ""

# Super admin tekshiruvi
def is_super_admin(user_id: int) -> bool:
    return user_id in SUPER_ADMINS

# Xabar yuborish va log qilish
async def send_response(message_or_callback: types.Message | CallbackQuery, text: str, reply_markup=None):
    logger.info(f"Response sent: {text[:50]}... to user_id={message_or_callback.from_user.id}")
    target = message_or_callback.message if isinstance(message_or_callback, CallbackQuery) else message_or_callback
    await target.answer(text, reply_markup=reply_markup)

# /admin komandasi
@dp.message_handler(commands=['admin'])
async def admin_command_handler(message: types.Message):
    user_id, username = get_user_info(message)
    logger.info(f"/admin komandasi yuborildi: user_id={user_id}")

    if not username:
        logger.info(f"User {user_id} username i yo‘q")
        await send_response(message, "🚫 Sizning username ingiz yo‘q! Iltimos, Telegram sozlamalarida username o‘rnating.")
        return

    if not admins_db.is_admin_exists(user_id, username):
        logger.info(f"User {user_id} (username: {username}) admin emas")
        await send_response(message, "🚫 Siz admin emassiz!")
        return

    admin_type = admins_db.get_admin_type(user_id)
    logger.info(f"User {user_id} admin turi: {admin_type}")
    # Super admin uchun maxsus menu, oddiy admin uchun umumiy menu
    reply_markup = admin_menu1 if is_super_admin(user_id) else admin_menu
    await send_response(message, f"👋 Admin paneliga xush kelibsiz, {admin_type}!\nKerakli bo‘limni tanlang:", reply_markup)

# Admin qo‘shish boshlash
@dp.message_handler(text="👮‍♂️ Admin Qo‘shish")
async def start_admin_actions(message: types.Message, state: FSMContext):
    user_id, _ = get_user_info(message)
    logger.info(f"Admin Qo‘shish tugmasi bosildi: user_id={user_id}")
    if not is_super_admin(user_id):
        logger.info(f"User {user_id} is not a super admin")
        await send_response(message, "🚫 Sizda bu bo‘limga kirish huquqi yo‘q!")
        return
    logger.info("Super admin tasdiqlandi, javob yuborilmoqda")
    await send_response(message, "Admin bilan ishlash bo‘limi:", admin_menu1)

# Admin qo‘shish handlerlari
@dp.message_handler(text=["➕ Admin qo'shish", "➕ Super admin qo'shish"])
async def add_admin_handler(message: types.Message, state: FSMContext):
    user_id, _ = get_user_info(message)
    logger.info(f"{message.text} tugmasi bosildi: user_id={user_id}")
    if not is_super_admin(user_id):
        logger.info(f"User {user_id} is not a super admin")
        await send_response(message, "🚫 Sizda bu amalni bajarish huquqi yo‘q!" if message.text == "➕ Admin qo'shish" else "🚫 Siz super admin emassiz, super admin qo‘sha olmaysiz!")
        return
    logger.info(f"Super admin tasdiqlandi, {message.text[2:].lower()} qo‘shish jarayoni boshlandi")
    state_name = AdminStates.super_admin if message.text == "➕ Super admin qo'shish" else AdminStates.admin
    await send_response(message, f"👤 Yangi {message.text[2:].lower()} qo‘shish uchun Telegram ID va username kiriting:\n\nMisol: 123456789 @username", admin_menu1)
    await state.update_data(admin_requester=user_id)
    await state_name.set()

# Admin qo‘shish jarayoni
@dp.message_handler(state=[AdminStates.admin, AdminStates.super_admin])
async def process_admin_add(message: types.Message, state: FSMContext):
    logger.info(f"Admin qo‘shish jarayoni: user_id={message.from_user.id}")
    user_data = await state.get_data()

    if message.from_user.id != user_data.get("admin_requester"):
        logger.info(f"User {message.from_user.id} is not the requester")
        return

    if message.text == "🔙 Admin menyu":
        await state.finish()
        logger.info("Jarayon bekor qilindi")
        await send_response(message, "Jarayon bekor qilindi.", admin_menu1 if is_super_admin(message.from_user.id) else admin_menu)
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        logger.info("Noto‘g‘ri format kiritildi")
        await send_response(message, "❌ Foydalanish tartibi:\n123456789 @username", admin_menu1)
        return

    try:
        telegram_id = int(args[0])
        full_name = args[1].strip()
        admin_type = "super_admin" if await state.get_state() == AdminStates.super_admin.state else "admin"
        admins_db.add_admin(telegram_id, full_name, admin_type)  # admin_type qo'shildi
        logger.info(f"Admin qo‘shildi: ID={telegram_id}, Type={admin_type}")
        await send_response(message, f"✅ {full_name} (ID: {telegram_id}) {admin_type} sifatida qo‘shildi!", admin_menu1)
    except ValueError:
        logger.info("Telegram ID noto‘g‘ri kiritildi")
        await send_response(message, "❌ Telegram ID faqat raqam bo‘lishi kerak!", admin_menu1)
    finally:
        await state.finish()

# Delete Admin tugmasi
@dp.message_handler(text="🗑 Delete Admin")
async def remove_admin_handler(message: types.Message):
    user_id, _ = get_user_info(message)
    logger.info(f"Delete Admin tugmasi bosildi: user_id={user_id}")
    if not is_super_admin(user_id):
        logger.info(f"User {user_id} is not a super admin")
        await send_response(message, "🚫 Sizda admin o‘chirish huquqi yo‘q!")
        return
    admins = admins_db.get_all_admins()
    if not admins:
        logger.info("Adminlar yo‘q")
        await send_response(message, "❌ Hozircha hech qanday admin yo‘q.", admin_menu1)
        return
    keyboard = InlineKeyboardMarkup(row_width=1)
    for admin in admins:
        admin_id = admin[0]
        admin_name = admin[1] if len(admin) > 1 else f"Admin {admin_id}"
        admin_type = admin[2] if len(admin) > 2 else "admin"
        keyboard.add(InlineKeyboardButton(f"{admin_name} ({admin_type})", callback_data=f"confirm_remove_admin:{admin_id}"))
    logger.info("Adminlar ro‘yxati yuborildi")
    await send_response(message, "🛑 O‘chirmoqchi bo‘lgan adminni tanlang:", keyboard)

# Adminni o‘chirish tasdiqlash
@dp.callback_query_handler(lambda c: c.data.startswith("confirm_remove_admin:"))
async def confirm_remove_admin(callback_query: CallbackQuery):
    user_id, _ = get_user_info(callback_query)
    logger.info(f"Admin o‘chirish tasdiqlash: user_id={user_id}")
    if not is_super_admin(user_id):
        logger.info(f"User {user_id} is not a super admin")
        await send_response(callback_query, "🚫 Sizda admin o‘chirish huquqi yo‘q!")
        return
    telegram_id = int(callback_query.data.split(":")[1])
    admins_db.delete_admin(telegram_id)
    logger.info(f"Admin o‘chirildi: ID={telegram_id}")
    await send_response(callback_query, f"✅ Admin (ID: {telegram_id}) o‘chirildi!", admin_menu1)

# Adminlar ro‘yxati
@dp.message_handler(text="👮‍♂️ Adminlar ro‘yxati")
async def list_admins_handler(message: types.Message):
    user_id, _ = get_user_info(message)
    logger.info(f"Adminlar ro‘yxati so‘raldi: user_id={user_id}")
    admins = admins_db.get_all_admins()
    if not admins:
        logger.info("Adminlar yo‘q")
        await send_response(message, "❌ Hali hech qanday admin yo‘q.", admin_menu)
        return
    response = f"👮‍♂️ Adminlar ro‘yxati:\n\n👨‍💼 Adminlar soni: {len(admins)}\n\n"
    response += "".join(f"🆔 {admin[0]} - {admin[1]} ({admin[2]})\n- - - - - - - - - - - - - - - - - -\n" for admin in admins)
    logger.info("Adminlar ro‘yxati yuborildi")
    await send_response(message, response, admin_menu)

# Admin menu
@dp.message_handler(text="Admin menu")
async def admin_menu_handler(message: types.Message):
    user_id, _ = get_user_info(message)
    logger.info(f"Admin menu tugmasi bosildi: user_id={user_id}")
    reply_markup = admin_menu1 if is_super_admin(user_id) else admin_menu
    await send_response(message, "Admin paneliga xush kelibsiz! Kerakli bo‘limni tanlang:", reply_markup)

# Ortga qaytish
@dp.message_handler(text="🔙 Ortga")
async def back_to_main_menu(message: types.Message):
    user_id, _ = get_user_info(message)
    logger.info(f"Ortga tugmasi bosildi: user_id={user_id}")
    reply_markup = admin_menu1 if is_super_admin(user_id) else admin_menu
    await send_response(message, "Asosiy menyuga qaytdingiz!", reply_markup)

# Kino qo‘shish
@dp.message_handler(text="➕ Kino Qo‘shish")
async def add_movie_handler(message: types.Message, state: FSMContext):
    user_id, _ = get_user_info(message)
    logger.info(f"Kino Qo‘shish tugmasi bosildi: user_id={user_id}")
    if not admins_db.is_admin_exists(user_id, message.from_user.username or ""):
        logger.info(f"User {user_id} is not an admin")
        await send_response(message, "🚫 Siz admin emassiz!")
        return
    await send_response(message, "🎥 Yangi kino qo‘shish uchun ma’lumotlarni kiriting:\n\nFormat: Kino nomi | Tavsif\nMisol: Avatar | Fantastik film", admin_menu)
    await state.update_data(movie_requester=user_id)
    await AdminStates.movie.set()

# Kino qo‘shish jarayoni
@dp.message_handler(state=AdminStates.movie)
async def process_add_movie(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    logger.info(f"Kino qo‘shish jarayoni: user_id={user_id}")
    user_data = await state.get_data()
    if user_id != user_data.get("movie_requester"):
        logger.info(f"User {user_id} is not the requester")
        return
    if message.text == "🔙 Admin menyu":
        await state.finish()
        logger.info("Jarayon bekor qilindi")
        await send_response(message, "Jarayon bekor qilindi.", admin_menu)
        return
    args = message.text.split("|", 1)
    if len(args) < 2:
        logger.info("Noto‘g‘ri format kiritildi")
        await send_response(message, "❌ Foydalanish tartibi:\nKino nomi | Tavsif", admin_menu)
        return
    title, description = map(str.strip, args)
    admins_db.add_movie(title, description, user_id)
    logger.info(f"Kino qo‘shildi: Title={title}")
    await send_response(message, f"✅ Kino qo‘shildi!\nNomi: {title}\nTavsif: {description}", admin_menu)
    await state.finish()

# Kino o‘chirish
@dp.message_handler(text="🗑 Kino O‘chirish")
async def delete_movie_handler(message: types.Message):
    user_id, _ = get_user_info(message)
    logger.info(f"Kino O‘chirish tugmasi bosildi: user_id={user_id}")
    if not admins_db.is_admin_exists(user_id, message.from_user.username or ""):
        logger.info(f"User {user_id} is not an admin")
        await send_response(message, "🚫 Siz admin emassiz!")
        return
    movies = admins_db.get_all_movies()
    if not movies:
        logger.info("Kinolar yo‘q")
        await send_response(message, "❌ Hozircha hech qanday kino yo‘q.", admin_menu)
        return
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*(InlineKeyboardButton(movie[1], callback_data=f"confirm_delete_movie:{movie[0]}") for movie in movies))
    logger.info("Kinolar ro‘yxati yuborildi")
    await send_response(message, "🛑 O‘chirmoqchi bo‘lgan kinoni tanlang:", keyboard)

# Kino o‘chirish tasdiqlash
@dp.callback_query_handler(lambda c: c.data.startswith("confirm_delete_movie:"))
async def confirm_delete_movie(callback_query: CallbackQuery):
    user_id, _ = get_user_info(callback_query)
    logger.info(f"Kino o‘chirish tasdiqlash: user_id={user_id}")
    if not admins_db.is_admin_exists(user_id, callback_query.from_user.username or ""):
        logger.info(f"User {user_id} is not an admin")
        await send_response(callback_query, "🚫 Siz admin emassiz!")
        return
    movie_id = int(callback_query.data.split(":")[1])
    admins_db.delete_movie(movie_id)
    logger.info(f"Kino o‘chirildi: ID={movie_id}")
    await send_response(callback_query, f"✅ Kino (ID: {movie_id}) o‘chirildi!", admin_menu)

# Statistika
@dp.message_handler(text="📊 Statistika")
async def statistics_handler(message: types.Message):
    user_id, _ = get_user_info(message)
    logger.info(f"Statistika tugmasi bosildi: user_id={user_id}")
    if not admins_db.is_admin_exists(user_id, message.from_user.username or ""):
        logger.info(f"User {user_id} is not an admin")
        await send_response(message, "🚫 Siz admin emassiz!")
        return
    admins = admins_db.get_all_admins()
    movies = admins_db.get_all_movies()
    response = f"📊 Statistika:\n\n👨‍💼 Adminlar soni: {len(admins)}\n🎥 Kinolar soni: {len(movies)}\n"
    logger.info("Statistika yuborildi")
    await send_response(message, response, admin_menu)

# Reklama
@dp.message_handler(text="📣 Reklama")
async def advertisement_handler(message: types.Message):
    user_id, _ = get_user_info(message)
    logger.info(f"Reklama tugmasi bosildi: user_id={user_id}")
    if not admins_db.is_admin_exists(user_id, message.from_user.username or ""):
        logger.info(f"User {user_id} is not an admin")
        await send_response(message, "🚫 Siz admin emassiz!")
        return
    await send_response(message, "📣 Reklama bo‘limi:\n\nBu bo‘limda reklamalarni boshqarish mumkin bo‘ladi. Hozircha test rejimida.", admin_menu)

# Kanallar
@dp.message_handler(text="📢 Kanallar")
async def channels_handler(message: types.Message):
    user_id, _ = get_user_info(message)
    logger.info(f"Kanallar tugmasi bosildi: user_id={user_id}")
    if not is_super_admin(user_id):
        logger.info(f"User {user_id} is not a super admin")
        await send_response(message, "🚫 Sizda bu bo‘limga kirish huquqi yo‘q!")
        return
    await send_response(message, "📢 Kanallar bo‘limi:\n\nBu bo‘limda kanallarni boshqarish mumkin bo‘ladi. Hozircha test rejimida.", admin_menu1)

# Middleware ni faollashtirish
setup_subscription_middleware()