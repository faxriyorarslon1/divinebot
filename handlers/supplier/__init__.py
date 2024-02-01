from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate, translate_cyrillic_or_latin
from Tranlate.translate_language import latin, russian
from api.orders import update_status, order_get_one_order
from api.product import get_one_product
from api.users import district_retrieve
from api.users.users import get_one_user
from button.inline import order_all_supplier, check_delivery
from button.reply_markup import back_menu, base_menu
from dispatch import dp
from states import BaseState, SupplierState


@dp.message_handler(lambda message: (str(message.text).__eq__(latin['BRON_SUPPLIER']) or str(message.text).__eq__(
    russian['BRON_SUPPLIER']) or str(message.text).__eq__(
    translate_cyrillic_or_latin(latin['BRON_SUPPLIER'], 'cyr'))) and (not str(message.text).__eq__('/start')),
                    state=BaseState.base)
async def delivery_menu_bron_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['page'] = 1
        text = translate(data['lang'], 'BRON_DELIVERY_MENU')
        text2 = translate(data['lang'], 'OR_THE_BACK')
        orders = order_all_supplier(data['token'], page=1, lang=data['lang'])
        if orders:
            await SupplierState.begin.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
            await message.bot.send_message(text=text2, chat_id=message.chat.id,
                                           reply_markup=order_all_supplier(token=data['token'], page=1,
                                                                           lang=data['lang']))
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.callback_query_handler(state=SupplierState.begin)
async def cal_delivery_handler(call: types.CallbackQuery, state: FSMContext):
    props = call.data
    async with state.proxy() as data:
        if props.__eq__("exit"):
            text = translate(data['lang'], 'BACK')
            await BaseState.base.set()
            user = get_one_user(data['user_id'])
            data['role'] = user['role']
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=base_menu(data['lang'], data['role']))
            return
        if props.__eq__("prev"):
            data['page'] -= 1
            text = translate(data['lang'], 'THE_ONE_BACK')
            await SupplierState.begin.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=order_all_supplier(page=data['page'],
                                                                                token=data['token']))
            return
        if props.__eq__("next"):
            data['page'] += 1
            text = translate(data['lang'], 'THE_ONE_NEXT')
            await SupplierState.begin.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=order_all_supplier(page=data['page'],
                                                                                token=data['token']))
            return
        data['order_id'] = props[1:]
        orders = order_get_one_order(data['order_id'], data['token'])
        status = orders['status']
        if status.__eq__('office_manager'):
            status = translate_cyrillic_or_latin("Offis Menedjer", data['lang'])
        elif status.__eq__('delivery'):
            status = translate_cyrillic_or_latin("Yetkazib beruvchida", data['lang'])
        elif status.__eq__('supplier'):
            status = translate_cyrillic_or_latin("Omborxonada", data['lang'])
        elif status.__eq__('manager'):
            status = translate_cyrillic_or_latin('MP/Menedjerda', data['lang'])
        user = get_one_user(orders['seller'])
        district = district_retrieve(user['district'])
        name = user['first_name']
        if user['last_name']:
            name = f"{user['first_name']} {user['last_name']}"
        text = f"{translate(data['lang'], 'COMPANY_NAME')}: {orders['company_name']}\nInn: {orders['inn']}\n{translate_cyrillic_or_latin('Status', data['lang'])}: {status}\n{translate(data['lang'], 'CREATOR')}: {name}\n{translate(data['lang'], 'DISTRICT')}: {translate_cyrillic_or_latin(district['name'], data['lang'], )}\n\t\t\t\t\t\t{translate(data['lang'], 'BASKET')}\n"
        for i, product_id in enumerate(orders['products'], start=1):
            product = get_one_product(product_id['product'], token=data['token'])
            text += f"{i}){translate(data['lang'], 'NAME')}: {product['name']}\n{translate(data['lang'], 'COUNT')}: {product_id['count']}\n{translate(data['lang'], 'PRICE')}({orders['type_price']}):{product['price1'] * product_id['count'] if orders['type_price'].__eq__('50%') else product['price2'] * product_id['count']}\n\n"
        text += f"{translate(data['lang'], 'TOTAL_PRICE')}({orders['type_price']}): {orders['total_price']}\n\n"
        await SupplierState.submit.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=check_delivery(data['lang']))


@dp.callback_query_handler(state=SupplierState.submit)
async def submit_status_for_delivery(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'SUCCESS')
        update_status(status='delivery',
                      order_id=data['order_id'],
                      token=data['token'])
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=base_menu(data['lang'], data['role']))
