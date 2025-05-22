from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Admin menu klaviaturasini yaratish
admin_menu = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
)
admin_menu.add(
    KeyboardButton("📊 Statistika"),
    KeyboardButton("➕ Kino Qo‘shish"),
    KeyboardButton("🗑 Kino O‘chirish"),
    KeyboardButton("📣 Reklama"),
    KeyboardButton("📢 Kanallar"),
    KeyboardButton("👮‍♂️ Admin Qo‘shish"),
    KeyboardButton("🗑 Delete Admin"),
    KeyboardButton("👮‍♂️ Adminlar ro‘yxati"),
    KeyboardButton("Admin menu")
)

# Super admin uchun maxsus menu
admin_menu1 = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
)
admin_menu1.add(
    KeyboardButton("➕ Admin qo'shish"),
    KeyboardButton("➕ Super admin qo'shish"),
    KeyboardButton("🔙 Ortga")
)