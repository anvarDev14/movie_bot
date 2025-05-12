from datetime import datetime

from aiogram import types
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.config import ADMINS
from keyboards.default.kanal_button import kanal_keyboard
from loader import dp, bot, user_db, channel_db
import asyncio
import logging

# Logging sozlamalari
logging.basicConfig(
    filename='bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Kanalda obuna tekshirish
async def check_subscription(user_id: int, channel_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Kanal {channel_id} da {user_id} tekshirishda xatolik: {e}")
        return False

# Barcha kanallarga obuna tekshiruvi
async def is_subscribed_to_all_channels(user_id: int) -> bool:
    channels = channel_db.get_all_channels()
    if not channels:
        return True  # Kanallar bo‘sh bo‘lsa, obuna talab qilinmaydi
    for channel_id, _, _ in channels:
        if not await check_subscription(user_id, channel_id):
            return False
    return True

# Obuna bo'lmagan kanallar ro'yxati
async def get_unsubscribed_channels(user_id: int) -> list:
    channels = channel_db.get_all_channels()
    if not channels:
        return []  # Agar kanallar bo‘sh bo‘lsa, bo‘sh ro‘yxat qaytaramiz
    return [(link, title) for channel_id, title, link in channels if not await check_subscription(user_id, channel_id)]

# Inline klaviatura
def get_subscription_keyboard(unsubscribed_channels):
    markup = InlineKeyboardMarkup(row_width=1)
    if unsubscribed_channels:  # Faqat ro‘yxat bo‘sh bo‘lmasa tugma qo‘shamiz
        for index, (invite_link, title) in enumerate(unsubscribed_channels, start=1):
            if invite_link.startswith("https://t.me/"):
                markup.add(InlineKeyboardButton(f"{index}. ➕ Obuna bo‘lish)", url=invite_link))
            else:
                markup.add(InlineKeyboardButton(f"{index}. ➕ Obuna bo‘lish", callback_data="no_action"))
        markup.add(InlineKeyboardButton("✅ Azo bo'ldim", callback_data="check_subscription"))
    return markup


# Qolgan kanallar haqida xabar
def get_remaining_channels_message(remaining_count):
    if remaining_count == 0:
        return "🎉 Barcha kanallarga obuna bo‘ldingiz!"
    else:
        return f"📌 Hali {remaining_count} ta kanalga obuna bo‘lishingiz kerak!"

# Avtomatik tekshirish va yangilash funksiyasi
async def auto_check_subscription(user_id: int, message: types.Message):
    while True:
        await asyncio.sleep(5)  # Har 5 soniyada tekshirish
        if await is_subscribed_to_all_channels(user_id):
            new_text = f"👋 Assalomu alaykum, {message.from_user.full_name}! Kino Botga xush kelibsiz.\n\n✍🏻 Kino kodini yuboring."
            if message.text != new_text:
                await message.edit_text(new_text, parse_mode="HTML")
            break
        else:
            unsubscribed = await get_unsubscribed_channels(user_id)
            new_text = "⚠️ <b>Siz hali barcha kanallarga obuna bo'lmadingiz!</b>\n\n👇 Quyidagilarga obuna bo'ling:"
            new_reply_markup = get_subscription_keyboard(unsubscribed)
            if message.text != new_text or message.reply_markup != new_reply_markup:
                await message.edit_text(new_text, reply_markup=new_reply_markup, parse_mode="HTML")

# Foydalanuvchini ro'yxatdan o'tkazish uchun alohida funksiya
async def register_user(user_id: int, username: str, context: str = "unknown") -> bool:
    try:
        if not user_db.select_user(user_id):
            user_db.add_user(user_id, username)
            user_count = user_db.count_users()
            logger.info(f"Yangi foydalanuvchi: @{username}, Jami: {user_count}, Context: {context}")


            # Adminlarga batafsil xabar yuborish
            for admin in ADMINS:
                try:
                    # Foydalanuvchi haqida qo‘shimcha ma’lumot olish
                    user_info = await bot.get_chat(user_id)
                    full_name = user_info.full_name if user_info.full_name else "Noma'lum"
                    join_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Ro‘yxatdan o‘tgan vaqt

                    # Chiroyli va to‘liq xabar
                    admin_message = (
                        "🔔 <b>Yangi foydalanuvchi qo‘shildi!</b>\n\n"
                        f"👤 <b>Username:</b> @{username}\n"
                        f"📛 <b>Ism:</b> {full_name}\n"
                        f"🆔 <b>ID:</b> {user_id}\n"
                        f"📅 <b>Ro‘yxatdan o‘tgan vaqt:</b> {join_date}\n"
                        f"👥 <b>Jami foydalanuvchilar:</b> {user_count}\n"
                        f"📍 <b>Kirish usuli:</b> {context}\n"
                        "────────────────────\n"
                        "<i>Botdan foydalanish boshlandi!</i>"
                    )
                    await bot.send_message(admin, admin_message, parse_mode="HTML")
                except Exception as e:
                    logger.error(f"Admin {admin} ga xabar yuborishda xatolik: {e}")
            return True
        else:
            user_db.update_last_active(user_id)
            logger.info(f"Foydalanuvchi {user_id} faolligi yangilandi, Context: {context}")
            return False
    except Exception as e:
        logger.error(f"Ro'yxatdan o'tkazishda xatolik (Context: {context}): {e}")
        raise

# /start komandasi
@dp.message_handler(CommandStart())
async def start_command(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name
    logger.info(f"/start from user_id={user_id}, username={username}")

    if message.chat.type != "private":
        await message.reply("Bot faqat shaxsiy chatda ishlaydi!")
        return

    # Admin tekshiruvi
    if user_id in ADMINS:
        await message.answer(
            f"👑 Admin {message.from_user.full_name}! Botga xush kelibsiz.\n✍🏻 Kino kodini yuboring.",
            reply_markup=kanal_keyboard
        )
        return

    # Foydalanuvchini ro‘yxatdan o‘tkazish (xabar yuborilmaydi)
    try:
        await register_user(user_id, username, context="/start")
    except Exception as e:
        logger.error(f"/start da ro'yxatdan o'tkazishda xatolik: {e}")
        await message.answer("⚠️ Ro‘yxatdan o‘tishda xatolik yuz berdi. Qayta urinib ko‘ring.")
        return

    # Kanallar ro‘yxatini tekshirish
    channels = channel_db.get_all_channels()
    if not channels:  # Agar kanal bo‘lmasa
        await message.answer(
            f"👋 Assalomu alaykum, {message.from_user.full_name}! Kino Botga xush kelibsiz.\n\n✍🏻 Kino kodini yuboring.",
            reply_markup=kanal_keyboard
        )
    else:  # Agar kanallar bo‘lsa, obuna tekshiruvi
        if await is_subscribed_to_all_channels(user_id):
            await message.answer(
                f"👋 Assalomu alaykum, {message.from_user.full_name}! Kino Botga xush kelibsiz.\n\n✍🏻 Kino kodini yuboring.",
                reply_markup=kanal_keyboard
            )
        else:
            unsubscribed = await get_unsubscribed_channels(user_id)
            text = "⚠️ <b>Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:</b>"
            markup = get_subscription_keyboard(unsubscribed)
            try:
                msg = await message.answer(text, reply_markup=markup, parse_mode="HTML")
                if unsubscribed:  # Faqat kanallar bo‘lsa avto-tekshirishni ishga tushiramiz
                    asyncio.create_task(auto_check_subscription(user_id, msg))
            except Exception as e:
                logger.error(f"Obuna xabarini yuborishda xatolik: {e}")
                await message.answer("Xatolik yuz berdi. Qayta urinib ko'ring.")

# Obuna tekshirish callback
@dp.callback_query_handler(lambda c: c.data == "check_subscription")
async def check_subscription_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    username = callback.from_user.username or callback.from_user.full_name

    if user_id in ADMINS:
        await callback.message.edit_text("👑 Siz adminsiz, obuna shart emas!", parse_mode="HTML")
        await callback.answer()
        return

    # Ikkinchi ro'yxatdan o'tkazish imkoniyati (xabar yuborilmaydi)
    try:
        await register_user(user_id, username, context="check_subscription")
    except Exception as e:
        await callback.message.edit_text("⚠️ Ro‘yxatdan o‘tishda xatolik yuz berdi. Qayta urinib ko‘ring.", parse_mode="HTML")
        await callback.answer()
        return

    # Obuna tekshiruvi
    if await is_subscribed_to_all_channels(user_id):
        await callback.message.edit_text(
            f"👋 Assalomu Alaykum, {callback.from_user.full_name}! Kino Botga xush kelibsiz.\n\n✍🏻 Kino kodini yuboring.",
            parse_mode="HTML"
        )
        await callback.answer()
    else:
        unsubscribed = await get_unsubscribed_channels(user_id)
        text = "⚠️ <b>Hali barcha kanallarga obuna bo‘lmadingiz!</b>\n\n👇 Quyidagilarga obuna bo'ling:"
        markup = get_subscription_keyboard(unsubscribed)
        await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
        await callback.answer("Obunani tekshiring!")

# "📽 Barcha kinolar" tugmasi
@dp.message_handler(lambda message: message.text == "📽 Barcha kinolar")
async def send_channel_link(message: types.Message):
    user_id = message.from_user.id
    if not user_db.select_user(user_id):
        await message.answer("⚠️ Avval ro‘yxatdan o‘ting! /start buyrug‘ini yuboring.")
        return
    await message.answer(
        "<b>🎬 Yangi kinolar:</b>\n📌 https://t.me/Kino_mania_2024",
        parse_mode="HTML"
    )

# Shaxsiy kanal uchun no_action callback
@dp.callback_query_handler(lambda c: c.data == "no_action")
async def no_action_callback(callback: types.CallbackQuery):
    await callback.answer("Bu shaxsiy kanal. Iltimos, kanal adminidan tasdiq so‘rang.", show_alert=True)
