from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("📊 Statistika"), KeyboardButton("➕ Kino Qo‘shish")],
        [KeyboardButton("🗑 Kino O‘chirish"), KeyboardButton("🔙 Admin menyu")],
        [KeyboardButton("📣 Reklama"),KeyboardButton("📢 Kanallar")],  # Alohida qator sifatida qo‘shildi
    ],
    resize_keyboard=True
)