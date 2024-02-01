from aiogram.dispatcher.filters.state import StatesGroup, State


class BronState(StatesGroup):
    begin = State()
    manager_send = State()
    final_create = State()
    bron = State()


class GetAllBronState(StatesGroup):
    check = State()
    confirmed = State()
    not_confirmed = State()
    begin = State()


class CreateBronState(StatesGroup):
    check = State()
    choice_price = State()
    inn = State()
    comment = State()
    choice_product_reply = State()
    count = State()
    reply_products = State()
    products = State()


class CreateCompanyState(StatesGroup):
    address = State()
    phone_number = State()
    bank_name = State()
    inn = State()
    name = State()


class CreateCompanyManagerState(StatesGroup):
    address = State()
    phone_number = State()
    bank_name = State()
    inn = State()
    name = State()


class UpdateBronState(StatesGroup):
    reply_products = State()
    type_update = State()
    delete = State()
    success_send_office_manager = State()
    check = State()
    update_product = State()
    delete_product = State()
    count = State()
    new_product_add = State()
    new_product = State()
    products = State()
    inn = State()
    comment = State()
    update = State()
    orders = State()


class BronReportState(StatesGroup):
    day = State()
    one = State()
    month = State()
    begin = State()


class VizitReportState(StatesGroup):
    day = State()
    location = State()
    member_list = State()
    begin = State()
    month = State()


class AdminVizitReportState(StatesGroup):
    village = State()
    begin = State()
    day = State()
    location = State()
    member_list = State()
    month = State()


class OrderUpdateState(StatesGroup):
    update_comment = State()
    choice_product_reply = State()
    check = State()
    count = State()
    type_update = State()
    new_product_or_delete = State()
    begin = State()
