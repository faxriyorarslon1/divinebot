from aiogram.dispatcher.filters.state import StatesGroup, State


class DebitState(StatesGroup):
    excel = State()
    begin = State()


class IncomeState(StatesGroup):
    excel = State()
    begin = State()


class OrdersState(StatesGroup):
    begin = State()


class GetAllProductState(StatesGroup):
    content = State()
    expiration_date = State()
    seria = State()
    image = State()
    price50 = State()
    price100 = State()
    status = State()
    count = State()
    name = State()
    original_count = State()
    delete = State()
    update = State()
    choice = State()
    reply_products = State()
    get_all = State()


class WarehouseState(StatesGroup):
    check = State()
    unreviewed = State()
    finish = State()
    confirmed = State()
    day = State()
    month = State()
    begin = State()


class CreateProductState(StatesGroup):
    product_image = State()
    the_rest = State()
    status = State()
    seria = State()
    expiration_date = State()
    original_count = State()
    price50 = State()
    price100 = State()
    name = State()
    content = State()


class CreateExcelState(StatesGroup):
    excel = State()
