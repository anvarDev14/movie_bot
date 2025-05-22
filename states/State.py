from aiogram.dispatcher.filters.state import StatesGroup, State


class AddAdmin(StatesGroup):
    admin = State()
    user_id = State()