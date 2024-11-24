from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard=InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Statistika 📊",callback_data='stats'),
            InlineKeyboardButton(text="Reklama 🪧",callback_data='ad'),
        ],
        [
            InlineKeyboardButton(text="Kinolar soni 🔢",callback_data='count_movie')
        ],
        [
            InlineKeyboardButton(text="Bugungi kinolar", callback_data="today"),
            InlineKeyboardButton(text="Shu haftadagi kinolar",callback_data="week"),
            InlineKeyboardButton(text="Shu oydagi kinolar",callback_data="month")
        ],
        [
            InlineKeyboardButton(text="Kino sozlamalar⚙️",callback_data='movie_settings')
        ]
    ]
)

settings=InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton("Kino qo'shish➕",callback_data='add_movie'),
            InlineKeyboardButton("Kinoni o'chirish➖",callback_data='delete_movie')
        ],
        [
            InlineKeyboardButton("Captionni o'zgartirish🔧",callback_data='edit_caption'),
            InlineKeyboardButton("Orqaga🔙",callback_data='admin_menu')
        ]
    ]
)

ad_menu=InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton("To'xtatish⏸️",callback_data="pause_ad"),
            InlineKeyboardButton("Yangilash🔃",callback_data='refresh_ad'),
            InlineKeyboardButton("Orqaga🔙",callback_data='admin_menu_ad')
        ]
    ]
)
