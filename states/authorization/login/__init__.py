from aiogram.dispatcher.filters.state import StatesGroup, State


class LoginState(StatesGroup):
    begin = State()
