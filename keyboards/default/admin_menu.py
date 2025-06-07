from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("📊 Statistika"), KeyboardButton("➕ Kino Qo‘shish")],
        [KeyboardButton("🗑 Kino O‘chirish"), KeyboardButton("🔙 Admin menyu")],
        [KeyboardButton("📣 Reklama"), KeyboardButton("📢 Kanallar")],
        [KeyboardButton("👤 Admin Qo‘shish"), KeyboardButton("🗑 Admin O‘chirish")],
        [KeyboardButton("📋 Adminlar Ro‘yxati")],
    ],
    resize_keyboard=True
)