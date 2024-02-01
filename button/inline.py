from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from Tranlate.tranlate_config import translate, translate_cyrillic_or_latin
from api.orders import order_get_all_order, order_get_one_order, delivery_orders, supplier_orders, get_confirmed_orders, \
    get_unreviewed_orders, get_not_agent_confirmed_orders, get_agent_confirmed_orders, \
    get_confirmed_orders_office_manager, get_unreviewed_orders_office_manager
from api.orders.company import Company
from api.orders.distict import district_order, worker_mp_agent, worker_order
from api.product import get_products, get_one_product, get_all_products
from api.users import district_get_all, all_city_for_district, district_retrieve
from api.users.city import city_doctor
from api.users.hospital import Hospital
from api.users.pharmacy import Pharmacy
from api.users.users import get_all_user_or_agent, get_all_not_active_member, get_role_member, get_mp_users, \
    get_manager_users
from handlers.dagavor_nomer import DOCTOR_TYPE
from utils import split_text
from utils.kunlar import month_day
from utils.oylar import OYLAR


def village_all_inline(lang):
    keyboard = InlineKeyboardMarkup()
    all_district = district_get_all()
    for i in all_district['results']:
        keyboard.add(
            InlineKeyboardButton(text=translate_cyrillic_or_latin(i["name"], lang), callback_data=f"a{i['id']}"))
    return None if len(all_district) == 0 else keyboard


def mp_or_agent(lang):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(translate(lang, 'AGENT'), callback_data='agent'))
    keyboard.add(InlineKeyboardButton(translate(lang, 'MANAGER'), callback_data='manager'))
    return keyboard


def users(role, district, token, lang):
    keyboard = InlineKeyboardMarkup()
    worker = worker_mp_agent(role=role, district=district, token=token)
    for i in worker:
        if i['first_name']:
            full_name = f"{i['first_name']}"
            if i['last_name']:
                full_name = f"{i['first_name']} {i['last_name']}"
            keyboard.add(
                InlineKeyboardButton(text=translate_cyrillic_or_latin(full_name, lang),
                                     callback_data=f"a{i['id']}"))
    keyboard.add(InlineKeyboardButton(text=translate(lang, 'BACK_MENU'), callback_data='back'))
    return None if len(worker) == 0 else keyboard


def user_role_order(user_id, day, month, token, lang):
    keyboard = InlineKeyboardMarkup()
    order = worker_order(user_id=user_id, day=day, month=month, token=token)
    for i in order:
        keyboard.add(InlineKeyboardButton(text=translate_cyrillic_or_latin(split_text(i['company_name']), lang),
                                          callback_data=f"a{i['id']}"))
    keyboard.add(InlineKeyboardButton(text=translate(lang, 'BACK_MENU'), callback_data=f"back"))
    return None if len(order) == 0 else keyboard


def order_village_inline(district, day, month, token, lang):
    keyboard = InlineKeyboardMarkup()
    district = district_order(district=district, day=day, month=month, token=token)
    for i in district:
        keyboard.add(
            InlineKeyboardButton(text=split_text(i["company_name"]),
                                 callback_data=f"a{i['id']}"))
    keyboard.add(InlineKeyboardButton(text=translate(lang, 'BACK_MENU'), callback_data='back'))
    return None if len(district) == 0 else keyboard


def city_all_inline(district_id, token, created_by, lang):
    all_city = all_city_for_district(district_id, created_by, token=token)
    keyboard = InlineKeyboardMarkup(row_width=1)
    for i in all_city['results']:
        keyboard.add(
            InlineKeyboardButton(text=translate_cyrillic_or_latin(i['name'], lang), callback_data=f'a{i["id"]}'))
    keyboard.add(InlineKeyboardButton(text=translate(lang, 'NEW_CREATE'), callback_data='new'))
    keyboard.add(InlineKeyboardButton(text=translate(lang, 'BACK_MENU'), callback_data='back'))
    return keyboard


def get_all_not_order_agent(token):
    keyboard = InlineKeyboardMarkup()
    get_all = get_not_agent_confirmed_orders(token=token)
    for i in get_all:
        keyboard.add(InlineKeyboardButton(text=split_text(i['company_name']), callback_data=f"a{i['id']}"))
    return None if len(get_all) == 0 else keyboard


def get_all_order_agent(token):
    keyboard = InlineKeyboardMarkup()
    get_all = get_agent_confirmed_orders(token=token)
    for i in get_all:
        # if i['company_name']:
        keyboard.add(InlineKeyboardButton(text=i['company_name'], callback_data=f"a{i['id']}"))
    return None if len(get_all) == 0 else keyboard


def hospital_all_inline(token, page=1, city=None, lang='lat'):
    all_hospital = Hospital(token=token, city=city).lists()
    keyboard = InlineKeyboardMarkup(row_width=3)
    length = all_hospital['count']
    first = 0
    while length > first and all_hospital['count'] > 0:
        if ((length - first) % 2 == 1) and length - first > 2:
            keyboard.add(InlineKeyboardButton(text=all_hospital['results'][first]['name'],
                                              callback_data=f"a{all_hospital['results'][first]['id']}"),
                         InlineKeyboardButton(text=all_hospital['results'][first + 1]['name'],
                                              callback_data=f"a{all_hospital['results'][first + 1]['id']}"))
        elif ((length - first) % 2 == 0) and length - first > 0:
            keyboard.add(InlineKeyboardButton(text=all_hospital['results'][first]['name'],
                                              callback_data=f"a{all_hospital['results'][first]['id']}"),
                         InlineKeyboardButton(text=all_hospital['results'][first + 1]['name'],
                                              callback_data=f"a{all_hospital['results'][first + 1]['id']}"))
        else:
            keyboard.add(InlineKeyboardButton(text=all_hospital['results'][first]['name'],
                                              callback_data=f"a{all_hospital['results'][first]['id']}"))
        first += 2
    if page != 1:
        keyboard.add(InlineKeyboardButton(text="⏮", callback_data="prev"))
    keyboard.add(InlineKeyboardButton(translate(lang, 'NEW_CREATE'), callback_data="new"))
    if all_hospital['count'] / page > 25:
        keyboard.add(InlineKeyboardButton(text="⏭", callback_data="next"))
    keyboard.add(InlineKeyboardButton(translate(lang, 'BACK_MENU'), callback_data="back"))
    return None if first == 0 else keyboard


def pharmacy_all_inline(token, page=1, city=None, lang='lat'):
    all_hospital = Pharmacy(token=token, city=city).lists()
    keyboard = InlineKeyboardMarkup(row_width=3)
    length = all_hospital['count']
    first = 0
    while length > first and all_hospital['count'] > 0:
        if ((length - first) % 2 == 1) and length - first > 2:
            keyboard.add(InlineKeyboardButton(text=all_hospital['results'][first]['name'],
                                              callback_data=f"a{all_hospital['results'][first]['id']}"),
                         InlineKeyboardButton(text=all_hospital['results'][first + 1]['name'],
                                              callback_data=f"a{all_hospital['results'][first + 1]['id']}"))
        elif ((length - first) % 2 == 0) and length - first > 0:
            keyboard.add(InlineKeyboardButton(text=all_hospital['results'][first]['name'],
                                              callback_data=f"a{all_hospital['results'][first]['id']}"),
                         InlineKeyboardButton(text=all_hospital['results'][first + 1]['name'],
                                              callback_data=f"a{all_hospital['results'][first + 1]['id']}"))
        else:
            keyboard.add(InlineKeyboardButton(text=all_hospital['results'][first]['name'],
                                              callback_data=f"a{all_hospital['results'][first]['id']}"))
        first += 2
    if page != 1:
        keyboard.add(InlineKeyboardButton(text="⏮", callback_data="prev"))
    keyboard.add(InlineKeyboardButton(translate(lang, 'NEW_CREATE'), callback_data="new"))
    if all_hospital['count'] / page > 25:
        keyboard.add(InlineKeyboardButton(text="⏭", callback_data="next"))
    keyboard.add(InlineKeyboardButton(translate(lang, 'BACK_MENU'), callback_data="back"))
    return keyboard


def doctor_all_inline(hospital, token, search="", lang='lat', page=1):
    doctors = city_doctor(hospital_id=hospital, token=token, page=page)
    if not search.__eq__(""):
        doctors = city_doctor(hospital_id=hospital, token=token, search=search)
        if doctors['count'] == 0:
            doctors = city_doctor(hospital_id=hospital, token=token, page=page)
    keyboard = InlineKeyboardMarkup(row_width=1)
    for doctor in doctors['results']:
        keyboard.add(
            InlineKeyboardButton(
                text=f"{doctor['name']}, {doctor['category_doctor']}, {doctor['type_doctor']}",
                callback_data=f"a{doctor['id']}"))
    if page != 1:
        keyboard.add(InlineKeyboardButton(text="⏮", callback_data="prev"))
    if doctors['count'] / page > 25:
        keyboard.add(InlineKeyboardButton(text="⏭", callback_data="next"))
    keyboard.add(InlineKeyboardButton(text=translate(lang, 'NEW_CREATE'), callback_data="new"))
    keyboard.add(InlineKeyboardButton(text=translate(lang, 'BACK_MENU'), callback_data="back"))
    return keyboard


def check_agreement(lang='lat'):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(InlineKeyboardButton(text=translate(lang, 'YES'), callback_data="yes"))
    keyboard.add(InlineKeyboardButton(text=translate(lang, 'NO'), callback_data="no"))
    return keyboard


def choice_type():
    keyboard = InlineKeyboardMarkup(row_width=5)
    keyboard.add(
        InlineKeyboardButton(text='1', callback_data='a1'),
        InlineKeyboardButton(text='2', callback_data='a2'),
        InlineKeyboardButton(text='3', callback_data='a3'),
        InlineKeyboardButton(text='4', callback_data='a4'),
        InlineKeyboardButton(text='5', callback_data='a5'),
    )
    keyboard.add(
        InlineKeyboardButton(text='6', callback_data='a6'),
        InlineKeyboardButton(text='7', callback_data='a7'),
        InlineKeyboardButton(text='8', callback_data='a8'),
        InlineKeyboardButton(text='9', callback_data='a9'),
        InlineKeyboardButton(text='10', callback_data='a10')
    )
    return keyboard


def all_product_inline(search="", page=1, token=None, lang='lat'):
    keyboard = InlineKeyboardMarkup(row_width=3)
    products = get_all_products(page=page, token=token)
    if products['count'] != 0:
        for product in products['results']:
            active = product.get('active')
            if active:
                active = "✅"
            else:
                active = "❌"
            keyboard.add(
                InlineKeyboardButton(text=f'{product.get("name")} {active}', callback_data=f"a{product.get('id')}"))
        if page != 1:
            keyboard.add(InlineKeyboardButton(text="⏮", callback_data="prev"))
        keyboard.add(InlineKeyboardButton(text=translate(lang, 'BACK_MENU'), callback_data="exit"))
        if products['count'] / page > 25:
            keyboard.add(InlineKeyboardButton(text="⏭", callback_data="next"))
        return keyboard
    return None


def office_manager_all_product_inline(page=1, token=None, lang=None):
    keyboard = InlineKeyboardMarkup(row_width=3)
    products = get_all_products(page=page, token=token)
    if products['count'] != 0:
        for product in products['results']:
            keyboard.add(InlineKeyboardButton(text=f'{product.get("name")}', callback_data=f"a{product.get('id')}"))
        if page != 1:
            keyboard.add(InlineKeyboardButton(text="⏮", callback_data="prev"))
        keyboard.add(InlineKeyboardButton(text=translate(lang, 'BACK_MENU'), callback_data="exit"))
        if products['count'] / page > 25:
            keyboard.add(InlineKeyboardButton(text="⏭", callback_data="next"))
        return keyboard
    return None


# def company_inline(page=1, search=None, token=None, lang=None):
#     keyboard = InlineKeyboardMarkup()
#
# def company_vizit_inline():
#

def company_all_residue(page=1, search=None, token=None, lang=None):
    keyboard = InlineKeyboardMarkup()
    company = Company(search=search, token=token, page=page).get_all()
    if company.get('count') != 0:
        for i in company['results']:
            keyboard.add(InlineKeyboardButton(i['company_name'],
                                              callback_data=f"a{i['id']}"))
        if page != 1:
            keyboard.add(InlineKeyboardButton(text="⏮", callback_data="prev"))
        if company['count'] / page > 40:
            keyboard.add(InlineKeyboardButton(text="⏭", callback_data="next"))
    # keyboard.add(InlineKeyboardButton(translate(lang, 'NEW_CREATE'), callback_data="new"))
    keyboard.add(InlineKeyboardButton(translate(lang, 'BACK_MENU'), callback_data="back"))
    return keyboard


def company_all_inline(page=1, search=None, token=None, lang=None):
    keyboard = InlineKeyboardMarkup()
    company = Company(search=search, token=token, page=page).get_all()
    if company.get('count') != 0:
        for i in company['results']:
            keyboard.add(InlineKeyboardButton(i['company_name'],
                                              callback_data=f"a{i['id']}"))
        if page != 1:
            keyboard.add(InlineKeyboardButton(text="⏮", callback_data="prev"))
        if company['count'] / page > 25:
            keyboard.add(InlineKeyboardButton(text="⏭", callback_data="next"))
    keyboard.add(InlineKeyboardButton(translate(lang, 'NEW_CREATE'), callback_data="new"))
    keyboard.add(InlineKeyboardButton(translate(lang, 'BACK_MENU'), callback_data="back"))
    return keyboard


def order_all_inline(token=None, search="", page=1, lang="cyr"):
    keyboard = InlineKeyboardMarkup()
    orders = order_get_all_order(token=token, search=search, page=page)
    if orders['count'] != 0:
        for product in orders['results']:
            keyboard.add(InlineKeyboardButton(
                text=f'{translate(lang, "COMPANY_NAME")}:{split_text(product.get("company_name"))}',
                # text=f'Korxona STIRI:{product.get("inn")}\n Izoh:{product.get("comment")}',
                callback_data=f"a{product.get('id')}"))
        if page != 1:
            keyboard.add(InlineKeyboardButton(text="⏮", callback_data="prev"))
        keyboard.add(InlineKeyboardButton(text=translate(lang, 'BACK_MENU'), callback_data="exit"))
        if orders['count'] / page > 25:
            keyboard.add(InlineKeyboardButton(text="⏭", callback_data="next"))
        return keyboard
    return "Uzr lekin ma'lumot topilmadi"


def order_all_delivery(token=None, page=1, lang='cyr'):
    keyboard = InlineKeyboardMarkup()
    orders = delivery_orders(token=token, page=page)
    if orders['count'] != 0:
        for product in orders['results']:
            keyboard.add(InlineKeyboardButton(
                text=f'{translate(lang, "COMPANY_NAME")}:{split_text(product.get("company_name"))}',
                # text=f'Korxona STIRI:{product.get("inn")}\n Izoh:{product.get("comment")}',
                callback_data=f"a{product.get('id')}"))
        if page != 1:
            keyboard.add(InlineKeyboardButton(text="⏮", callback_data="prev"))
        keyboard.add(InlineKeyboardButton(text=translate(lang, 'BACK_MENU'), callback_data="exit"))
        if orders['count'] / page > 25:
            keyboard.add(InlineKeyboardButton(text="⏭", callback_data="next"))
        return keyboard
    return None


def order_all_supplier(token=None, page=1, lang='cyr'):
    keyboard = InlineKeyboardMarkup()
    orders = supplier_orders(token=token, page=page)
    if orders['count'] != 0:
        for product in orders['results']:
            keyboard.add(InlineKeyboardButton(
                text=f'{translate(lang, "COMPANY_NAME")}:{split_text(product.get("company_name"))}',
                # text=f'Korxona STIRI:{product.get("inn")}\n Izoh:{product.get("comment")}',
                callback_data=f"a{product.get('id')}"))
        if page != 1:
            keyboard.add(InlineKeyboardButton(text="⏮", callback_data="prev"))
        keyboard.add(InlineKeyboardButton(text=translate(lang, 'BACK_MENU'), callback_data="exit"))
        if orders['count'] / page > 25:
            keyboard.add(InlineKeyboardButton(text="⏭", callback_data="next"))
        return keyboard
    return None


def order_update_all_inline(token=None, search="", page=1, send_manager=True, lang='lat'):
    keyboard = InlineKeyboardMarkup()
    orders = order_get_all_order(token=token, search=search, page=page, manager_send=send_manager)
    if orders['count'] != 0:
        for product in orders['results']:
            keyboard.add(InlineKeyboardButton(
                text=f'{translate(lang, "COMPANY_NAME")}:{split_text(product.get("company_name"))}',
                callback_data=f"a{product.get('id')}"))
            keyboard.add()
        if page != 1:
            keyboard.add(InlineKeyboardButton(text=translate(lang, "PREV"), callback_data="prev"))
        keyboard.add(InlineKeyboardButton(text=translate(lang, "EXIT"), callback_data="exit"))
        if orders['count'] / page > 25:
            keyboard.add(InlineKeyboardButton(text=translate(lang, "NEXT"), callback_data="next"))
        return keyboard
    return None


def order_product_all(order_id, token, lang):
    keyboard = InlineKeyboardMarkup()
    order_one = order_get_one_order(order_id=order_id, token=token)
    for order in order_one['products']:
        product = get_one_product(product_id=order['product'], token=token)
        keyboard.add(
            InlineKeyboardButton(
                text=f"{translate(text='NAME', lang=lang)}:{translate_cyrillic_or_latin(product['name'], lang)}\t{translate(lang, 'COUNT')}:{order['count']}",
                callback_data=f"a{product['id']}b{order['count']}"))
    keyboard.add(InlineKeyboardButton(text=translate(lang, text="BACK_MENU"), callback_data="back"))
    return keyboard


def doctor_type_inline_button(lang):
    keyboard = InlineKeyboardMarkup(row_width=3)
    last = 39
    first = 0
    while last > first + 3:
        keyboard.add(InlineKeyboardButton(text=translate_cyrillic_or_latin(DOCTOR_TYPE[first], lang),
                                          callback_data=translate_cyrillic_or_latin(DOCTOR_TYPE[first], lang)),
                     InlineKeyboardButton(text=translate_cyrillic_or_latin(DOCTOR_TYPE[first + 1], lang),
                                          callback_data=translate_cyrillic_or_latin(DOCTOR_TYPE[first + 1], lang)),
                     InlineKeyboardButton(text=translate_cyrillic_or_latin(DOCTOR_TYPE[first + 2], lang),
                                          callback_data=translate_cyrillic_or_latin(DOCTOR_TYPE[first + 2], lang)))
        first += 3
    keyboard.add(InlineKeyboardButton(text=translate_cyrillic_or_latin(DOCTOR_TYPE[first], lang),
                                      callback_data=translate_cyrillic_or_latin(DOCTOR_TYPE[first], lang)),
                 InlineKeyboardButton(text=translate_cyrillic_or_latin(DOCTOR_TYPE[first + 1], lang),
                                      callback_data=translate_cyrillic_or_latin(DOCTOR_TYPE[first + 1], lang)),
                 InlineKeyboardButton(text=translate_cyrillic_or_latin(DOCTOR_TYPE[first + 2], lang),
                                      callback_data=translate_cyrillic_or_latin(DOCTOR_TYPE[first + 2], lang)))
    keyboard.add(InlineKeyboardButton(text=translate(lang, "BACK_MENU"), callback_data="back"))
    return keyboard


def category_doctor_inline(lang):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text=translate_cyrillic_or_latin("AC", lang)[0],
                                      callback_data=translate_cyrillic_or_latin("AC", lang)[0]))
    keyboard.add(InlineKeyboardButton(text=translate_cyrillic_or_latin("BC", lang)[0],
                                      callback_data=translate_cyrillic_or_latin("BC", lang)[0]))
    keyboard.add(InlineKeyboardButton(text=translate_cyrillic_or_latin("CC", lang)[0],
                                      callback_data=translate_cyrillic_or_latin("CC", lang)[0]))
    keyboard.add(InlineKeyboardButton(text=translate(lang, 'BACK_MENU'), callback_data="back"))
    return keyboard


def create_count():
    keyboard = InlineKeyboardMarkup(row_width=4)
    keyboard.add(InlineKeyboardButton(text='1', callback_data=f"a1"),
                 InlineKeyboardButton(text='3', callback_data=f"a3"),
                 InlineKeyboardButton(text='5', callback_data=f"a5"),
                 InlineKeyboardButton(text='10', callback_data=f"a10"))
    keyboard.add(InlineKeyboardButton(text='16', callback_data=f"a16"),
                 InlineKeyboardButton(text='32', callback_data=f"a32"),
                 InlineKeyboardButton(text='50', callback_data=f"a50"),
                 InlineKeyboardButton(text='70', callback_data=f"a70")
                 )
    keyboard.add(InlineKeyboardButton(text='100', callback_data=f"a100"),
                 InlineKeyboardButton(text='150', callback_data=f"a150"),
                 InlineKeyboardButton(text='200', callback_data=f"a200"),
                 InlineKeyboardButton(text='400', callback_data=f"a400")
                 )
    keyboard.add(InlineKeyboardButton(text='600', callback_data=f"a600"),
                 InlineKeyboardButton(text='800', callback_data=f"a800"),
                 InlineKeyboardButton(text='1000', callback_data=f"a1000"),
                 InlineKeyboardButton(text='2000', callback_data=f"a2000")
                 )

    return keyboard


def get_all_agent(lang, token, page, first_name, district):
    keyboard = InlineKeyboardMarkup()
    if first_name:
        first_name = translate_cyrillic_or_latin(first_name, 'lat')
    get_all = get_mp_users(district=district, first_name=first_name, page=page, token=token)
    for get_one in get_all['results']:
        if get_one['first_name']:
            full_name = f"{get_one['first_name']}"
            if get_one['last_name']:
                full_name = f"{get_one['first_name']} {get_one['last_name']}"
            keyboard.add(
                InlineKeyboardButton(text=translate_cyrillic_or_latin(text=full_name, lang=lang),
                                     callback_data=f"a{get_one['id']}"))
    if page != 1:
        keyboard.add(InlineKeyboardButton(text="⏮", callback_data="prev"))
    if get_all['count'] / page > 25:
        keyboard.add(InlineKeyboardButton(text="⏭", callback_data="next"))
    return None if get_all['count'] == 0 else keyboard


def get_all_manager(lang, token, page, district):
    keyboard = InlineKeyboardMarkup()
    get_all = get_manager_users(district=district, page=page, token=token)
    for get_one in get_all['results']:
        if get_one['first_name']:
            full_name = f"{get_one['first_name']}"
            if get_one['last_name']:
                full_name = f"{get_one['first_name']} {get_one['last_name']}"
            keyboard.add(
                InlineKeyboardButton(text=f"{translate_cyrillic_or_latin(text=full_name, lang=lang)})",
                                     callback_data=f"a{get_one['id']}"))
    if page != 1:
        keyboard.add(InlineKeyboardButton(text="⏮", callback_data="prev"))
    if get_all['count'] / page > 25:
        keyboard.add(InlineKeyboardButton(text="⏭", callback_data="next"))
    return None if get_all['count'] == 0 else keyboard


def product_reply_markup(lang, product_list):
    keyboard = InlineKeyboardMarkup()
    for product in product_list:
        keyboard.add(InlineKeyboardButton(text=translate_cyrillic_or_latin(product.get('name'), lang),
                                          callback_data=product.get("id")))
    keyboard.add(InlineKeyboardButton(text=translate(lang, 'BACK_MENU'), callback_data="back"))
    return keyboard


def check_basket(lang='lat'):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text=translate(lang, "YES"), callback_data="yes"))
    keyboard.add(InlineKeyboardButton(text=translate(lang, "NO"), callback_data="no"))
    return keyboard


def choice_product(lang):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text=translate(lang=lang, text='ADD_BASKET'), callback_data="yes"))
    keyboard.add(InlineKeyboardButton(text=translate(lang, "PREV"), callback_data='no'))
    return keyboard


def create_inn_choice(lang):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text=translate(lang, "NEXT"), callback_data="yes"))
    return keyboard


def get_confirmed_orders_inline(day, month, token, lang):
    keyboard = InlineKeyboardMarkup()
    orders = get_confirmed_orders(token, day, month)
    for order in orders:
        keyboard.add(InlineKeyboardButton(split_text(order['company_name']),
                                          callback_data=f'a{order["id"]}'))
    return None if len(orders) == 0 else keyboard


def get_confirmed_orders_office_manager_inline(day, month, token, lang):
    keyboard = InlineKeyboardMarkup()
    orders = get_confirmed_orders_office_manager(token, day, month)
    for order in orders:
        keyboard.add(InlineKeyboardButton(split_text(order['company_name']),
                                          callback_data=f'a{order["id"]}'))
    return None if len(orders) == 0 else keyboard


def get_unreviewed_orders_inline(day, month, token, lang):
    keyboard = InlineKeyboardMarkup()
    orders = get_unreviewed_orders(token, day, month)
    for order in orders:
        keyboard.add(InlineKeyboardButton(split_text(order['company_name']),
                                          callback_data=f'a{order["id"]}'))
    return None if len(orders) == 0 else keyboard


def get_unreviewed_orders_inline_office_manager(day, month, token, lang):
    keyboard = InlineKeyboardMarkup()
    orders = get_unreviewed_orders_office_manager(token, day, month)
    for order in orders:
        keyboard.add(InlineKeyboardButton(split_text(order['company_name']),
                                          callback_data=f'a{order["id"]}'))
    return None if len(orders) == 0 else keyboard


# print(all_product_inline(token="6c49382fc5c3c6e4ddf4393861586f78331c2e8f"))
def choice_price_markup(price1, price2, lang):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text=f"50%: {price1} {translate(lang, 'SUM')}", callback_data="price1"))
    keyboard.add(InlineKeyboardButton(text=f"100%: {price2} {translate(lang, 'SUM')}", callback_data="price2"))
    keyboard.add(InlineKeyboardButton(text=translate(lang, 'CHOICE'), callback_data="no"))
    return keyboard


def choice_order_type():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Mahsulotlar", callback_data="products"))
    keyboard.add(InlineKeyboardButton(text="Comment", callback_data="comment"))
    # keyboard.add(InlineKeyboardButton(text="STIR(INN)", callback_data="inn"))
    keyboard.add(InlineKeyboardButton(text="Orqaga", callback_data="back"))
    return keyboard


def language_choice(lang):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text=translate('lat', "LATIN"), callback_data="lat"))
    keyboard.add(InlineKeyboardButton(text=translate('lat', "CYRIL"), callback_data="cyr"))
    keyboard.add(InlineKeyboardButton(text=translate('lat', "RUSSIAN"), callback_data="ru"))
    return keyboard


def choice_order_params():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Qo'shish", callback_data="create"))
    keyboard.add(InlineKeyboardButton(text="Olib Tashlash", callback_data="delete"))
    keyboard.add(InlineKeyboardButton(text="Orqaga", callback_data="back"))
    return keyboard


def months(lang):
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(InlineKeyboardButton(text=translate_cyrillic_or_latin(OYLAR[0], lang), callback_data=f"a1"),
                 InlineKeyboardButton(text=translate_cyrillic_or_latin(OYLAR[1], lang), callback_data=f"a2"),
                 InlineKeyboardButton(text=translate_cyrillic_or_latin(OYLAR[2], lang), callback_data=f"a3"))
    keyboard.add(InlineKeyboardButton(text=translate_cyrillic_or_latin(OYLAR[3], lang), callback_data=f"a4"),
                 InlineKeyboardButton(text=translate_cyrillic_or_latin(OYLAR[4], lang), callback_data=f"a5"),
                 InlineKeyboardButton(text=translate_cyrillic_or_latin(OYLAR[5], lang), callback_data=f"a6"))

    keyboard.add(InlineKeyboardButton(text=translate_cyrillic_or_latin(OYLAR[6], lang), callback_data=f"a7"),
                 InlineKeyboardButton(text=translate_cyrillic_or_latin(OYLAR[7], lang), callback_data=f"a8"),
                 InlineKeyboardButton(text=translate_cyrillic_or_latin(OYLAR[8], lang), callback_data=f"a9")
                 )
    keyboard.add(InlineKeyboardButton(text=translate_cyrillic_or_latin(OYLAR[9], lang), callback_data=f"a10"),
                 InlineKeyboardButton(text=translate_cyrillic_or_latin(OYLAR[10], lang), callback_data=f"a11"),
                 InlineKeyboardButton(text=translate_cyrillic_or_latin(OYLAR[11], lang), callback_data=f"a12")
                 )
    return keyboard.add()


def member_list_inline(lang, district):
    keyboard = InlineKeyboardMarkup()
    members = get_all_user_or_agent(district)
    for member in members['results']:
        if member['first_name']:
            name = f"{member['first_name']}"
            if member['last_name']:
                name = f"{member['first_name']} {member['last_name']}"
            keyboard.add(
                InlineKeyboardButton(text=translate_cyrillic_or_latin(name, lang),
                                     callback_data=f"a{member.get('id')}"))
    return None if members['count'] == 0 else keyboard


def role_member(lang):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(text=translate_cyrillic_or_latin("Office Menejer", lang), callback_data='office_manager'))
    keyboard.add(
        InlineKeyboardButton(text=translate_cyrillic_or_latin("Omborxona Menejer", lang), callback_data='delivery'))
    keyboard.add(
        InlineKeyboardButton(text=translate_cyrillic_or_latin("Menejer", lang), callback_data='manager'))
    keyboard.add(
        InlineKeyboardButton(text=translate_cyrillic_or_latin("Tibbiy Vakil", lang), callback_data='agent'))
    keyboard.add(
        InlineKeyboardButton(text=translate_cyrillic_or_latin("Yetkazib beruvchi", lang), callback_data='supplier'))
    keyboard.add(InlineKeyboardButton(text=translate(lang, 'BACK_MENU'), callback_data="back"))
    return keyboard


def call_debit(page, file, lang):
    keyboard = InlineKeyboardMarkup()
    if page != 1:
        keyboard.add(InlineKeyboardButton(text="⏮", callback_data="prev"))
    if len(file) / page > 25:
        keyboard.add(InlineKeyboardButton(text="⏭", callback_data="next"))
    keyboard.add(InlineKeyboardButton(text=translate(lang, 'BACK_MENU'), callback_data="back"))
    return keyboard


def get_all_not_active_inline(lang):
    keyboard = InlineKeyboardMarkup()
    get_all_users = get_all_not_active_member()
    for member in get_all_users:
        if member['first_name']:
            name = f"{member.get('first_name')}"
            if member['last_name']:
                name = f"{member.get('first_name')} {member.get('last_name')}"
            district = district_retrieve(member['district'])
            keyboard.add(
                InlineKeyboardButton(
                    text=f"{translate_cyrillic_or_latin(name, lang)}({translate_cyrillic_or_latin(district['name'], lang)})",
                    callback_data=f"a{member.get('id')}"))
    keyboard.add(InlineKeyboardButton(text=translate(lang, 'BACK_MENU'), callback_data="back"))
    return keyboard


def get_all_user_member(lang, role):
    keyboard = InlineKeyboardMarkup()
    get_all_roles = get_role_member(role)
    for member in get_all_roles:
        if member['first_name']:
            name = f"{member.get('first_name')}"
            if member['last_name']:
                name = f"{member.get('first_name')} {member.get('last_name')}"
            district = district_retrieve(member['district'])
            keyboard.add(
                InlineKeyboardButton(
                    text=f'{translate_cyrillic_or_latin(name, lang)}({translate_cyrillic_or_latin(district["name"], lang)})',
                    callback_data=f"a{member.get('id')}"))
    keyboard.add(InlineKeyboardButton(text=translate(lang, 'BACK_MENU'), callback_data="back"))
    return keyboard


def role_choice(lang):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(translate(lang, 'CREATE_ROLE'), callback_data='create_role'))
    keyboard.add(InlineKeyboardButton(text=translate(lang, 'BACK_MENU'), callback_data="back"))
    return keyboard


def update_employed_menu(lang):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(translate(lang, "UPDATE_ROLE"), callback_data='update_role'))
    keyboard.add(InlineKeyboardButton(translate(lang, "DELETE_EMPLOYED"), callback_data='delete_employed'))
    keyboard.add(InlineKeyboardButton(translate(lang, "UPDATE_USER_DATA"), callback_data='update_user_data'))
    keyboard.add(
        InlineKeyboardButton(translate(lang, "UPDATE_USER_DATA_LAST_NAME"), callback_data='update_user_data_last_name'))
    keyboard.add(InlineKeyboardButton(translate(lang, "UPDATE_PHONE_NUMBER"), callback_data='update_phone_number'))
    keyboard.add(InlineKeyboardButton(translate(lang, 'DISTRICT_UPDATE'), callback_data='update_district'))
    keyboard.add(InlineKeyboardButton(text=translate(lang, 'BACK_MENU'), callback_data="back"))
    return keyboard


def status(lang):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(translate(lang=lang, text="YES_ACTIVE"), callback_data='active'))
    keyboard.add(InlineKeyboardButton(translate(lang=lang, text="NO_ACTIVE"), callback_data='no_active'))
    return keyboard


def get_month_day(month):
    keyboard = InlineKeyboardMarkup(row_width=8)
    months_ = month_day(month)
    if len(months_) == 30:
        keyboard.add(
            InlineKeyboardButton(text=months_[0], callback_data=f"a{months_[0]}"),
            InlineKeyboardButton(text=months_[1], callback_data=f"a{months_[1]}"),
            InlineKeyboardButton(text=months_[2], callback_data=f"a{months_[2]}"),
            InlineKeyboardButton(text=months_[3], callback_data=f"a{months_[3]}"),
            InlineKeyboardButton(text=months_[4], callback_data=f"a{months_[4]}"),
            InlineKeyboardButton(text=months_[5], callback_data=f"a{months_[5]}"),
            InlineKeyboardButton(text=months_[6], callback_data=f"a{months_[6]}"),
            InlineKeyboardButton(text=months_[7], callback_data=f"a{months_[7]}"),
            InlineKeyboardButton(text=months_[8], callback_data=f"a{months_[8]}"),
            InlineKeyboardButton(text=months_[9], callback_data=f"a{months_[9]}"),
            InlineKeyboardButton(text=months_[10], callback_data=f"a{months_[10]}"),
            InlineKeyboardButton(text=months_[11], callback_data=f"a{months_[11]}"),
            InlineKeyboardButton(text=months_[12], callback_data=f"a{months_[12]}"),
            InlineKeyboardButton(text=months_[13], callback_data=f"a{months_[13]}"),
            InlineKeyboardButton(text=months_[14], callback_data=f"a{months_[14]}"),
            InlineKeyboardButton(text=months_[15], callback_data=f"a{months_[15]}"),
            InlineKeyboardButton(text=months_[16], callback_data=f"a{months_[16]}"),
            InlineKeyboardButton(text=months_[17], callback_data=f"a{months_[17]}"),
            InlineKeyboardButton(text=months_[18], callback_data=f"a{months_[18]}"),
            InlineKeyboardButton(text=months_[19], callback_data=f"a{months_[19]}"),
            InlineKeyboardButton(text=months_[20], callback_data=f"a{months_[20]}"),
            InlineKeyboardButton(text=months_[21], callback_data=f"a{months_[21]}"),
            InlineKeyboardButton(text=months_[22], callback_data=f"a{months_[22]}"),
            InlineKeyboardButton(text=months_[23], callback_data=f"a{months_[23]}"),
            InlineKeyboardButton(text=months_[24], callback_data=f"a{months_[24]}"),
            InlineKeyboardButton(text=months_[25], callback_data=f"a{months_[25]}"),
            InlineKeyboardButton(text=months_[26], callback_data=f"a{months_[26]}"),
            InlineKeyboardButton(text=months_[27], callback_data=f"a{months_[27]}"),
            InlineKeyboardButton(text=months_[28], callback_data=f"a{months_[28]}"),
            InlineKeyboardButton(text=months_[29], callback_data=f"a{months_[29]}"),

        )
    if len(months_) == 31:
        keyboard.add(
            InlineKeyboardButton(text=months_[0], callback_data=f"a{months_[0]}"),
            InlineKeyboardButton(text=months_[1], callback_data=f"a{months_[1]}"),
            InlineKeyboardButton(text=months_[2], callback_data=f"a{months_[2]}"),
            InlineKeyboardButton(text=months_[3], callback_data=f"a{months_[3]}"),
            InlineKeyboardButton(text=months_[4], callback_data=f"a{months_[4]}"),
            InlineKeyboardButton(text=months_[5], callback_data=f"a{months_[5]}"),
            InlineKeyboardButton(text=months_[6], callback_data=f"a{months_[6]}"),
            InlineKeyboardButton(text=months_[7], callback_data=f"a{months_[7]}"),
            InlineKeyboardButton(text=months_[8], callback_data=f"a{months_[8]}"),
            InlineKeyboardButton(text=months_[9], callback_data=f"a{months_[9]}"),
            InlineKeyboardButton(text=months_[10], callback_data=f"a{months_[10]}"),
            InlineKeyboardButton(text=months_[11], callback_data=f"a{months_[11]}"),
            InlineKeyboardButton(text=months_[12], callback_data=f"a{months_[12]}"),
            InlineKeyboardButton(text=months_[13], callback_data=f"a{months_[13]}"),
            InlineKeyboardButton(text=months_[14], callback_data=f"a{months_[14]}"),
            InlineKeyboardButton(text=months_[15], callback_data=f"a{months_[15]}"),
            InlineKeyboardButton(text=months_[16], callback_data=f"a{months_[16]}"),
            InlineKeyboardButton(text=months_[17], callback_data=f"a{months_[17]}"),
            InlineKeyboardButton(text=months_[18], callback_data=f"a{months_[18]}"),
            InlineKeyboardButton(text=months_[19], callback_data=f"a{months_[19]}"),
            InlineKeyboardButton(text=months_[20], callback_data=f"a{months_[20]}"),
            InlineKeyboardButton(text=months_[21], callback_data=f"a{months_[21]}"),
            InlineKeyboardButton(text=months_[22], callback_data=f"a{months_[22]}"),
            InlineKeyboardButton(text=months_[23], callback_data=f"a{months_[23]}"),
            InlineKeyboardButton(text=months_[24], callback_data=f"a{months_[24]}"),
            InlineKeyboardButton(text=months_[25], callback_data=f"a{months_[25]}"),
            InlineKeyboardButton(text=months_[26], callback_data=f"a{months_[26]}"),
            InlineKeyboardButton(text=months_[27], callback_data=f"a{months_[27]}"),
            InlineKeyboardButton(text=months_[28], callback_data=f"a{months_[28]}"),
            InlineKeyboardButton(text=months_[29], callback_data=f"a{months_[29]}"),
            InlineKeyboardButton(text=months_[30], callback_data=f"a{months_[30]}"),

        )
    if len(months_) == 29:
        keyboard.add(
            InlineKeyboardButton(text=months_[0], callback_data=f"a{months_[0]}"),
            InlineKeyboardButton(text=months_[1], callback_data=f"a{months_[1]}"),
            InlineKeyboardButton(text=months_[2], callback_data=f"a{months_[2]}"),
            InlineKeyboardButton(text=months_[3], callback_data=f"a{months_[3]}"),
            InlineKeyboardButton(text=months_[4], callback_data=f"a{months_[4]}"),
            InlineKeyboardButton(text=months_[5], callback_data=f"a{months_[5]}"),
            InlineKeyboardButton(text=months_[6], callback_data=f"a{months_[6]}"),
            InlineKeyboardButton(text=months_[7], callback_data=f"a{months_[7]}"),
            InlineKeyboardButton(text=months_[8], callback_data=f"a{months_[8]}"),
            InlineKeyboardButton(text=months_[9], callback_data=f"a{months_[9]}"),
            InlineKeyboardButton(text=months_[10], callback_data=f"a{months_[10]}"),
            InlineKeyboardButton(text=months_[11], callback_data=f"a{months_[11]}"),
            InlineKeyboardButton(text=months_[12], callback_data=f"a{months_[12]}"),
            InlineKeyboardButton(text=months_[13], callback_data=f"a{months_[13]}"),
            InlineKeyboardButton(text=months_[14], callback_data=f"a{months_[14]}"),
            InlineKeyboardButton(text=months_[15], callback_data=f"a{months_[15]}"),
            InlineKeyboardButton(text=months_[16], callback_data=f"a{months_[16]}"),
            InlineKeyboardButton(text=months_[17], callback_data=f"a{months_[17]}"),
            InlineKeyboardButton(text=months_[18], callback_data=f"a{months_[18]}"),
            InlineKeyboardButton(text=months_[19], callback_data=f"a{months_[19]}"),
            InlineKeyboardButton(text=months_[20], callback_data=f"a{months_[20]}"),
            InlineKeyboardButton(text=months_[21], callback_data=f"a{months_[21]}"),
            InlineKeyboardButton(text=months_[22], callback_data=f"a{months_[22]}"),
            InlineKeyboardButton(text=months_[23], callback_data=f"a{months_[23]}"),
            InlineKeyboardButton(text=months_[24], callback_data=f"a{months_[24]}"),
            InlineKeyboardButton(text=months_[25], callback_data=f"a{months_[25]}"),
            InlineKeyboardButton(text=months_[26], callback_data=f"a{months_[26]}"),
            InlineKeyboardButton(text=months_[27], callback_data=f"a{months_[27]}"),
            InlineKeyboardButton(text=months_[28], callback_data=f"a{months_[28]}"),

        )
    if len(months_) == 28:
        keyboard.add(
            InlineKeyboardButton(text=months_[0], callback_data=f"a{months_[0]}"),
            InlineKeyboardButton(text=months_[1], callback_data=f"a{months_[1]}"),
            InlineKeyboardButton(text=months_[2], callback_data=f"a{months_[2]}"),
            InlineKeyboardButton(text=months_[3], callback_data=f"a{months_[3]}"),
            InlineKeyboardButton(text=months_[4], callback_data=f"a{months_[4]}"),
            InlineKeyboardButton(text=months_[5], callback_data=f"a{months_[5]}"),
            InlineKeyboardButton(text=months_[6], callback_data=f"a{months_[6]}"),
            InlineKeyboardButton(text=months_[7], callback_data=f"a{months_[7]}"),
            InlineKeyboardButton(text=months_[8], callback_data=f"a{months_[8]}"),
            InlineKeyboardButton(text=months_[9], callback_data=f"a{months_[9]}"),
            InlineKeyboardButton(text=months_[10], callback_data=f"a{months_[10]}"),
            InlineKeyboardButton(text=months_[11], callback_data=f"a{months_[11]}"),
            InlineKeyboardButton(text=months_[12], callback_data=f"a{months_[12]}"),
            InlineKeyboardButton(text=months_[13], callback_data=f"a{months_[13]}"),
            InlineKeyboardButton(text=months_[14], callback_data=f"a{months_[14]}"),
            InlineKeyboardButton(text=months_[15], callback_data=f"a{months_[15]}"),
            InlineKeyboardButton(text=months_[16], callback_data=f"a{months_[16]}"),
            InlineKeyboardButton(text=months_[17], callback_data=f"a{months_[17]}"),
            InlineKeyboardButton(text=months_[18], callback_data=f"a{months_[18]}"),
            InlineKeyboardButton(text=months_[19], callback_data=f"a{months_[19]}"),
            InlineKeyboardButton(text=months_[20], callback_data=f"a{months_[20]}"),
            InlineKeyboardButton(text=months_[21], callback_data=f"a{months_[21]}"),
            InlineKeyboardButton(text=months_[22], callback_data=f"a{months_[22]}"),
            InlineKeyboardButton(text=months_[23], callback_data=f"a{months_[23]}"),
            InlineKeyboardButton(text=months_[24], callback_data=f"a{months_[24]}"),
            InlineKeyboardButton(text=months_[25], callback_data=f"a{months_[25]}"),
            InlineKeyboardButton(text=months_[26], callback_data=f"a{months_[26]}"),
            InlineKeyboardButton(text=months_[27], callback_data=f"a{months_[27]}"),
        )
    return keyboard


def choice_office_manager(lang):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text=translate(lang, 'EDIT_PRODUCT'), callback_data='edit'))
    keyboard.add(InlineKeyboardButton(text=translate(lang, 'DELETE_PRODUCT'), callback_data='delete'))
    keyboard.add(InlineKeyboardButton(text=translate(lang, 'BACK_MENU'), callback_data='back'))
    return keyboard


def how_to_edit_for_product(lang):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(translate(lang, 'NAME'), callback_data='name'),
        InlineKeyboardButton(translate(lang, 'CONTENT'), callback_data='content'),
    )
    keyboard.add(
        InlineKeyboardButton(translate(lang, 'CREATE_PRODUCT_IMAGE'), callback_data='image'),
        InlineKeyboardButton(translate(lang, 'PRICE50%'), callback_data='price50'),
    )
    keyboard.add(
        InlineKeyboardButton(translate(lang, 'PRICE100%'), callback_data='price100'),
        InlineKeyboardButton(translate(lang, 'EXPIRATION_DATE'), callback_data='expiration_date'),
    )
    keyboard.add(
        InlineKeyboardButton(translate(lang, 'SERIA'), callback_data='seria'),
        InlineKeyboardButton(translate(lang, 'STATUS'), callback_data='status'),
    )
    keyboard.add(
        InlineKeyboardButton(translate(lang, 'ORIGINAL_COUNT'), callback_data='original_count'),
        InlineKeyboardButton(translate(lang, 'COUNT'), callback_data='count')
    )
    keyboard.add(
        InlineKeyboardButton(translate(lang, 'BACK_MENU'), callback_data='back'),
    )
    return keyboard


def is_active_inline(lang):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text=translate(lang, 'YES_ACTIVE'), callback_data='active'))
    keyboard.add(InlineKeyboardButton(text=translate(lang, 'NO_ACTIVE'), callback_data='no_active'))
    return keyboard


def check_delivery(lang):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text=translate(lang, 'SUBMIT'), callback_data='success'))
    return keyboard
