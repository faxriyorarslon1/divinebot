from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from Tranlate.tranlate_config import translate


def to_wait_func(lang):
    row1 = [KeyboardButton(text=translate(lang, text="WAIT"))]
    keyboard = [row1]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)


def register_markup(lang):
    row1 = [KeyboardButton(text=translate(lang=lang, text="REGISTER"))]
    keyboard = [row1]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)


def login(lang):
    row1 = [KeyboardButton(text=translate(lang=lang, text="LOGIN"))]
    keyboard = [row1]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)


def send_update_menu(lang):
    row1 = [KeyboardButton(text=translate(text="DELETE_ORDER", lang=lang))]
    row2 = [KeyboardButton(text=translate(lang, 'SEND_OFFICE_MANAGER'))]
    row3 = [KeyboardButton(text=translate(lang, 'ORDER_UPDATE_COMMENT_PRODUCTS'))]
    row4 = [KeyboardButton(text=translate(lang, 'BACK_MENU'))]
    keyboard = [row1, row2, row3, row4]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)


def update_order(lang):
    row1 = [KeyboardButton(text=translate(lang, 'UPDATE_COMMENT'))]
    row2 = [KeyboardButton(text=translate(lang, 'UPDATE_PRODUCT'))]
    row3 = [KeyboardButton(text=translate(lang, 'BACK_MENU'))]
    keyboard = [row1, row2, row3]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)


def new_or_delete_product(lang):
    row1 = [KeyboardButton(text=translate(lang, 'NEW_PRODUCT_CREATE'))]
    # row2 = [KeyboardButton(text=translate(lang, 'DELETE_PRODUCT'))]
    row3 = [KeyboardButton(text=translate(lang, 'BACK_MENU'))]
    keyboard = [row1, row3]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)


def bron_menu(lang):
    row = [KeyboardButton(translate(lang=lang, text='CREATE_ORDER'))]
    # KeyboardButton(text=translate(lang, 'UPDATE_ORDER'))]
    row2 = [KeyboardButton(text=translate(lang, 'GET_ALL_ORDERS_AGENT'))]
    row1 = [KeyboardButton(translate(lang, 'BACK_MENU'))]
    keyboard = [row, row2, row1]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)


# "CONFIRMED_AGENT_ORDERS": "✅ Подтвержденный",
#     "UNCONFIRMED_AGENT_ORDERS": "❓ Не подтверждено"
def bron_confirmed_or_unconfirmed_menu(lang):
    row = [KeyboardButton(translate(lang, 'CONFIRMED_AGENT_ORDERS')),
           KeyboardButton(translate(lang, "UNCONFIRMED_AGENT_ORDERS"))]
    row1 = [KeyboardButton(translate(lang, "BACK_MENU"))]
    keyboard = [row, row1]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)


def hospital_or_vizit(lang):
    row = [KeyboardButton(translate(text="PHARMACY", lang=lang)),
           KeyboardButton(translate(text='MANAGER_VIZIT', lang=lang))]
    row2 = [KeyboardButton(translate(text='BACK_MENU', lang=lang))]
    keyboard = [row, row2]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)


def search_markup(lang):
    row1 = [KeyboardButton(translate(text='SEARCH', lang=lang))]
    keyboard = [row1]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)


def phone_number_markup(lang):
    row = [KeyboardButton(text=translate(lang, 'PHONE_NUMBER'), request_contact=True)]
    keyboard = [row]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)


def admin_document(lang):
    row1 = [KeyboardButton(translate(lang, 'MANAGER_DOCUMENT')), KeyboardButton(translate(lang, 'MANAGER_LOCATION'))]
    row2 = [KeyboardButton(translate(lang, 'BACK_MENU'))]
    keyboard = [row1, row2]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)


def base_menu(lang, role: str):
    keyboard = []
    if role.__eq__("agent"):
        row1 = [KeyboardButton(translate(lang, "VIZIT")),
                KeyboardButton(translate(lang, "BRON"))]
        row2 = [KeyboardButton(translate(lang, "DOGOVOR")),
                KeyboardButton(translate(lang, "QARZDORLIK_AGENT"))]
        row3 = [KeyboardButton(translate(lang, 'INCOME_AGENT')),
                KeyboardButton(translate(lang, 'HOSPITAL_RESIDUE')),
                KeyboardButton(translate(lang, 'SETTINGS'))]
        keyboard = [row1, row2, row3]
    elif role.__eq__('manager'):
        row1 = [KeyboardButton(translate(lang, 'VIZIT_REPORT')), KeyboardButton(translate(lang, 'BRON_REPORT'))]
        row3 = [KeyboardButton(translate(lang, "BRON")), KeyboardButton(translate(lang, "DOUBLE_VIZIT"))]
        row4 = [KeyboardButton(translate(lang, 'SETTINGS')), KeyboardButton(translate(lang, 'HOSPITAL_PARAMS'))]
        keyboard = [row1, row3, row4]
    elif role.__eq__("admin"):
        row1 = [KeyboardButton(translate(lang, "EMPLOYED")), KeyboardButton(translate(lang, "NEW_EMPLOYED"))]
        row2 = [KeyboardButton(translate(lang, "TEST_EXCEL")), KeyboardButton(translate(lang, 'ADMIN_VIZIT_REPORT'))]
        row3 = [KeyboardButton(translate(lang, 'SETTINGS')), KeyboardButton(translate(lang, 'ADMIN_VIZIT_RESIDUE_SEE'))]
        keyboard = [row1, row2, row3]
    elif role.__eq__("office_manager"):
        row1 = [KeyboardButton(translate(lang, 'PRODUCTS')),
                KeyboardButton(translate(lang, 'WAREHOUSE'))]
        row2 = [KeyboardButton(translate(lang, 'INCOME')),
                KeyboardButton(translate(lang, 'QARZDORLIK'))]
        row3 = [KeyboardButton(translate(lang, 'OFFICE_MANAGER_CONTRACT_NUMBER_EXCEL')),
                KeyboardButton(translate(lang, 'SETTINGS'))]
        keyboard = [row1, row2, row3]
    elif role.__eq__('delivery'):
        row1 = [KeyboardButton(translate(lang, 'BRON_DELIVERY'))]
        row2 = [KeyboardButton(translate(lang, 'SETTINGS'))]
        keyboard = [row1, row2]
    elif role.__eq__('supplier'):
        row1 = [KeyboardButton(translate(lang, 'BRON_SUPPLIER'))]
        row2 = [KeyboardButton(translate(lang, 'SETTINGS'))]
        keyboard = [row1, row2]
    else:
        row1 = [KeyboardButton(translate(lang, 'WAIT'))]
        keyboard = [row1]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)


def create_or_read_contract_number(lang):
    row1 = [KeyboardButton(translate(lang, 'CREATE_CONTRACT_NUMBER')),
            KeyboardButton(translate(lang, 'READ_CONTRACT_NUMBER'))]
    row2 = [KeyboardButton(translate(lang, 'BACK_MENU'))]
    keyboard = [row1, row2]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)


def contract_number_menu(lang):
    row1 = [KeyboardButton(translate(lang, 'BUY_CONTRACT_NUMBER'))]
    row2 = [KeyboardButton(translate(lang, 'GET_CONTRACT_NUMBER'))]
    row3 = [KeyboardButton(translate(lang, 'BACK_MENU'))]
    keyboard = [row1, row2, row3]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)


def bron_report_menu(lang):
    # row = [KeyboardButton(translate(lang, "EXCEL_FORMAT"))]
    row2 = [KeyboardButton(translate(lang, "TEXT_FORMAT"))]
    row3 = [KeyboardButton(translate(lang, "BACK_MENU"))]
    keyboard = [row2, row3]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)


def back_menu(lang):
    row = [KeyboardButton(translate(lang, 'BACK_MENU')), KeyboardButton(translate(lang, 'HOME_BACK'))]
    keyboard = [row]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)


def location_menu_for_vizit(lang):
    row2 = [KeyboardButton(translate(lang, 'VIZIT_TEXT'))]
    row3 = [KeyboardButton(translate(lang, 'BACK_MENU'))]
    keyboard = [row2, row3]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)


def location_markup(lang):
    row1 = [KeyboardButton(translate(lang, "LOCATION"), request_location=True)]
    keyboard = [row1]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)


def settings_menu(lang):
    row1 = [KeyboardButton(translate(lang, "LANGUAGE_BUTTON"))]
    # row2 = [KeyboardButton(translate(lang, "USER_INFORMATION"))]
    row3 = [KeyboardButton(translate(lang, 'BACK_MENU'))]
    keyboard = [row1, row3]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)


def choice_bron_report(lang):
    row1 = [KeyboardButton(translate(lang, 'DOCUMENT_FILE'))]
    row2 = [KeyboardButton(translate(lang, 'GEOLOCATION_DOCUMENT'))]
    row3 = [KeyboardButton(translate(lang, 'BACK_MENU'))]
    keyboard = [row1, row2, row3]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)


def choice_vizit_report(lang):
    row1 = [KeyboardButton(translate(lang, 'VIZIT_DOCUMENT'))]
    row2 = [KeyboardButton(translate(lang, 'VIZIT_TELEGRAM'))]
    row3 = [KeyboardButton(translate(lang, 'BACK_MENU'))]
    keyboard = [row1, row2, row3]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)


def crud_for_office_manager(lang):
    row1 = [KeyboardButton(translate(lang, "CREATE_PRODUCT"))]
    row4 = [KeyboardButton(translate(lang, "GET_ALL_PRODUCT"))]
    row3 = [KeyboardButton(translate(lang, 'EXCEL_CREATE'))]
    row5 = [KeyboardButton(translate(lang, "BACK_MENU"))]
    keyboard = [row1, row4, row3, row5]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)


def office_manager_orders(lang):
    row1 = [KeyboardButton(translate(lang, 'CONFIRMED_ORDERS')), KeyboardButton(translate(lang, 'UNREVIEWED_ORDERS'))]
    row2 = [KeyboardButton(translate(lang, 'BY_PROVINCES')), KeyboardButton(translate(lang, 'BY_WORKERS'))]
    row3 = [KeyboardButton(translate(lang, 'BACK_MENU'))]
    keyboard = [row1, row2, row3]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)


def manager_hospital_residue(lang):
    row1 = [KeyboardButton(translate(lang, 'EXCEL_PATH')), KeyboardButton(translate(lang, 'EXCEL_TEXT'))]
    row2 = [KeyboardButton(translate(lang, 'BACK_MENU')), KeyboardButton(translate(lang, 'HOME_BACK'))]
    keyboard = [row1, row2]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)
