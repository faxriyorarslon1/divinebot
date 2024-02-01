from aiogram.dispatcher.filters.state import StatesGroup, State


class LocationState(StatesGroup):
    double_location = State()
    location = State()
