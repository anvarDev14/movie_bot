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
