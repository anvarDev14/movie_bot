from aiogram.types import ReplyKeyboardMarkup,KeyboardButton


menu_movie=ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="✅Tasdiqlash"),
            KeyboardButton(text="❌Bekor qilish"),
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True

)



