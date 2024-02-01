from aiogram.dispatcher.filters.state import StatesGroup, State


class DistrictWarehouseState(StatesGroup):
    check = State()
    finish = State()
    begin = State()


class WorkerWarehouseState(StatesGroup):
    check = State()
    order_worker = State()
    worker = State()
    finish = State()
    begin = State()


class SupplierState(StatesGroup):
    submit = State()
    begin = State()


class BaseState(StatesGroup):
    base = State()


class ManagerHospitalVizit(StatesGroup):
    begin = State()


class ContractNumberAllState(StatesGroup):
    create = State()
    begin = State()


class DebitState(StatesGroup):
    base = State()


class AdminDocumentState(StatesGroup):
    base = State()


class AdminLocationState(StatesGroup):
    day = State()
    workers = State()
    month = State()
    begin = State()


class ManagerIncomeState(StatesGroup):
    day = State()
    month = State()
    begin = State()


class HospitalResidueState(StatesGroup):
    inn = State()
    begin = State()


class HospitalResidueManagerState(StatesGroup):
    inn = State()
    begin = State()


class ProductResidueState(StatesGroup):
    new_reply_product = State()
    new_products = State()
    new_begin = State()
    new_product = State()
    reply_product = State()
    product = State()
    begin = State()


class ProductResidueManagerState(StatesGroup):
    new_reply_product = State()
    new_products = State()
    new_begin = State()
    new_product = State()
    reply_product = State()
    product = State()
    begin = State()


class CreateCompanyBossesState(StatesGroup):
    check = State()
    provider_name = State()
    provider_phone = State()
    director_phone = State()
    director_name = State()


class CreateCompanyBossesManagerState(StatesGroup):
    check = State()
    provider_name = State()
    provider_phone = State()
    director_phone = State()
    director_name = State()


class DeliveryState(StatesGroup):
    submit = State()
    reply_products = State()
    bron = State()
    begin = State()


class NewEmployedState(StatesGroup):
    pending = State()
    update_role = State()
    new = State()
    begin = State()


class EmployedState(StatesGroup):
    update_last_name = State()
    update_phone = State()
    update_name = State()
    update_district = State()
    finished = State()
    delete_user = State()
    update_role = State()
    update = State()
    member = State()
    begin = State()


class ContractNumberState(StatesGroup):
    get_contract_number = State()
    company_name = State()
    set_inn = State()
    begin = State()


class IncomeAgentState(StatesGroup):
    begin = State()
