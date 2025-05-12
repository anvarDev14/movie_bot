from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kanal_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📽 Barcha kinolar"),
        ],
    ],
    resize_keyboard=True,  # Tugmani moslashtirilgan hajmga mos qiladi
)

