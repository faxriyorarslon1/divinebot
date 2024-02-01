from aiogram.dispatcher.filters.state import StatesGroup, State


class SettingState(StatesGroup):
    language = State()
    begin = State()
