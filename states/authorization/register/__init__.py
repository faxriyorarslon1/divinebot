from aiogram.dispatcher.filters.state import StatesGroup, State


class RegisterState(StatesGroup):
    language = State()
    login = State()
    to_wait = State()
    password_image = State()
    phone_number = State()
    village = State()
    last_name = State()
    first_name = State()
    begin = State()
