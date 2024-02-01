from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import latin, russian
from api.orders import order_get_one_order
from api.product import get_one_product
from api.users import district_retrieve
from api.users.users import get_one_user
from button.inline import get_confirmed_orders_inline, get_confirmed_orders_office_manager_inline
from button.reply_markup import back_menu, base_menu, office_manager_orders
from dispatch import dp
from states import BaseState
# from handlers import back_manu
from states.orders import WarehouseState, DebitState, IncomeState
from utils.number_split_for_price import price_split


@dp.message_handler(lambda message: (str(message.text).__eq__(latin['CONFIRMED_ORDERS']) or str(message.text).__eq__(
    russian['CONFIRMED_ORDERS']) or str(message.text).__eq__(
    translate_cyrillic_or_latin(latin['CONFIRMED_ORDERS'], 'cyr'))) and (not str(message.text).__eq__('/start')),
                    state=WarehouseState.day)
async def confirmed_data_for_day_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'CONFIRMED_ORDERS_TEXT')
        text2 = translate(data['lang'], 'OR_THE_BACK')
        orders = get_confirmed_orders_office_manager_inline(day=data['day'], month=data['month'],
                                                            token=data['token'], lang=data['lang'])
        if orders:
            await WarehouseState.confirmed.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
            await message.bot.send_message(text=text2, chat_id=message.chat.id,
                                           reply_markup=orders)
            return
        text = translate(data['lang'], 'NOT_FOUND')
        await WarehouseState.day.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=office_manager_orders(data['lang']))


@dp.callback_query_handler(state=WarehouseState.confirmed)
async def confirmed_message_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['order_id'] = call.data[1:]
        order = order_get_one_order(data['order_id'], data['token'])
        status = order['status']
        if status.__eq__('office_manager'):
            status = translate_cyrillic_or_latin("Offis Menedjer", data['lang'])
        elif status.__eq__('delivery'):
            status = translate_cyrillic_or_latin("Yetkazib beruvchida", data['lang'])
        elif status.__eq__('supplier'):
            status = translate_cyrillic_or_latin("Omborxonada", data['lang'])
        elif status.__eq__('manager'):
            status = translate_cyrillic_or_latin('MP/Menedjerda', data['lang'])
        user = get_one_user(order['seller'])
        district = district_retrieve(user['district'])
        name = user['first_name']
        if user['last_name']:
            name = f"{user['first_name']} {user['last_name']}"
        text = f"{translate(data['lang'], 'COMPANY_NAME')}: {order['company_name']}\nInn: {order['inn']}\n{translate_cyrillic_or_latin('Status', data['lang'])}: {status}\n{translate(data['lang'], 'CREATOR')}: {name}\n{translate(data['lang'], 'DISTRICT')}: {translate_cyrillic_or_latin(district['name'], data['lang'])}\n\t\t\t\t\t\t{translate(data['lang'], 'BASKET')}\n"
        for i, product in enumerate(order['products'], start=1):
            product_one = get_one_product(product['product'], data['token'])
            text += f"{i}){translate(data['lang'], 'NAME')}: {product_one['name']}\n{translate(data['lang'], 'COUNT')}: {product['count']}\n{translate(data['lang'], 'PRICE')}({order['type_price']}):{price_split(product_one['price1'] * product['count']) if order['type_price'].__eq__('50%') else price_split(product_one['price2'] * product['count'])} {translate(data['lang'], 'SUM')}\n\n"
        text += f"\n{translate(data['lang'], 'CREATED_DATE')}:{str(order['created_date'][:10]) + ' ' + order['created_date'][11:16]}\n{translate(data['lang'], 'TOTAL_PRICE')}({order['type_price']}): {price_split(order['total_price'])} {translate(data['lang'], 'SUM')}\n\n"
        await WarehouseState.finish.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id)


@dp.message_handler(lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
    russian['BACK_MENU']) or str(message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                                            not str(message.text).__eq__('/start')),
                    state=[WarehouseState.finish, DebitState.excel, DebitState.begin, IncomeState.excel])
async def back_menu_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], "BASE_MENU_BACK")
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))
