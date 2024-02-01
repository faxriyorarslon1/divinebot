from aiogram.dispatcher.filters.state import StatesGroup, State


class VizitState(StatesGroup):
    checked = State()
    create_hospital = State()
    lpu = State()
    search = State()
    agreement = State()
    comment = State()
    doctor = State()
    vizit = State()


class DoctorState(StatesGroup):
    type = State()
    category = State()
    phone_number = State()
    begin = State()


class CityState(StatesGroup):
    create_address = State()
    create = State()
