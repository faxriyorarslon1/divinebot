from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import latin, russian
from api.orders import order_get_one_order, update_status
from api.product import get_one_product, update_product
from api.users import district_retrieve
from api.users.excel_for_order import OrderExcel
from api.users.users import get_one_user
from button.inline import order_all_delivery, check_delivery
from button.reply_markup import base_menu, back_menu
from dispatch import dp
from excel_utils.order import add_excel_product, edit_excel_data
from states import BaseState, DeliveryState
from utils.number_split_for_price import price_split


@dp.message_handler(lambda message: (str(message.text).__eq__(latin['BRON_DELIVERY']) or str(message.text).__eq__(
    russian['BRON_DELIVERY']) or str(message.text).__eq__(
    translate_cyrillic_or_latin(latin['BRON_DELIVERY'], 'cyr'))) and (not str(message.text).__eq__('/start')),
                    state=BaseState.base)
async def delivery_menu_bron_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['page'] = 1
        text = translate(data['lang'], 'BRON_DELIVERY_MENU')
        text2 = translate(data['lang'], 'OR_THE_BACK')
        orders = order_all_delivery(data['token'], page=1, lang=data['lang'])
        if orders:
            await DeliveryState.begin.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
            await message.bot.send_message(text=text2, chat_id=message.chat.id,
                                           reply_markup=order_all_delivery(token=data['token'], page=1,
                                                                           lang=data['lang']))
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.callback_query_handler(state=DeliveryState.begin)
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
            await DeliveryState.begin.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=order_all_delivery(page=data['page'],
                                                                                token=data['token']))
            return
        if props.__eq__("next"):
            data['page'] += 1
            text = translate(data['lang'], 'THE_ONE_NEXT')
            await DeliveryState.begin.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=order_all_delivery(page=data['page'],
                                                                                token=data['token']))
            return
        data['order_id'] = props[1:]
        orders = order_get_one_order(data['order_id'], data['token'])
        seller = get_one_user(orders['seller'])
        district = district_retrieve(seller['district'])
        name = f"{seller['first_name']}"
        if seller['last_name']:
            name = f"{seller['first_name']} {seller['last_name']}"
        text = f"{translate(data['lang'], 'COMPANY_NAME')}: {orders['company_name']}\nInn:{orders['inn']}\n{translate(data['lang'], 'CREATOR')}: {translate_cyrillic_or_latin(name, data['lang'])}\n{translate(data['lang'], 'DISTRICT')}: {translate_cyrillic_or_latin(district['name'], data['lang'])}\n\t\t\t\t\t\t{translate(data['lang'], 'BASKET')}\n"
        for i, product_id in enumerate(orders['products'], start=1):
            product = get_one_product(product_id['product'], token=data['token'])
            text += f"{i}){translate(data['lang'], 'NAME')}: {product['name']}\n{translate(data['lang'], 'COUNT')}: {price_split(product_id['count'])}\n{translate(data['lang'], 'PRICE')}({orders['type_price']}):{price_split(product['price1'] * product_id['count']) if orders['type_price'].__eq__('50%') else price_split(product['price2'] * product_id['count'])} {translate(data['lang'], 'SUM')}\n\n"
        text += f"\n{translate(data['lang'], 'CREATED_DATE')}:{str(orders['created_date'][:10]) + ' ' + orders['created_date'][11:16]}\n{translate(data['lang'], 'TOTAL_PRICE')}({orders['type_price']}): {price_split(orders['total_price'])} {translate(data['lang'], 'SUM')}\n\n"
        await DeliveryState.submit.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=check_delivery(data['lang']))


@dp.callback_query_handler(state=DeliveryState.submit)
async def submit_status_for_delivery(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        order = OrderExcel(token=data['token']).get_excel()
        if order:
            text = translate(data['lang'], 'SUCCESS')
            file = add_excel_product(order['file_name'])
            if file:
                update_status(status='manager',
                              order_id=data['order_id'],
                              token=data['token'])
                order_one = order_get_one_order(token=data['token'], order_id=data['order_id'])
                for i in order_one['products']:
                    product_one = get_one_product(i['product'], data['token'])
                    product = product_one.get("id")
                    name = product_one.get('name')
                    composition = product_one.get('composition')
                    active = product_one.get("active")
                    count = product_one.get("count")
                    warehouse_count = product_one.get('warehouse_count') - i['count']
                    original_count = product_one.get("original_count")
                    expiration_date = product_one.get("expired_date")[:10]
                    image = product_one.get('image')
                    price1 = product_one.get("price1")
                    price2 = product_one.get("price2")
                    seria = product_one.get("seria")
                    data['name'] = name
                    data['composition'] = composition
                    data['active'] = active
                    data['count_product'] = count
                    data['original_count'] = original_count
                    data['expiration_date'] = expiration_date
                    data['price1'] = price1
                    data['price2'] = price2
                    data['seria'] = seria
                    data['image'] = image
                    data['product_id'] = product
                    update_product(name=name, composition=composition, count=count, original_count=original_count,
                                   price1=price1,
                                   price2=price2, expired_date=expiration_date, seria=seria,
                                   active=product_one.get("active"),
                                   image=image,
                                   product_id=product, token=data['token'],
                                   created_by=product_one.get('created_by'),
                                   warehouse_count=warehouse_count)
                    product = get_one_product(product_id=i['product'], token=data['token'])
                    for j in file:
                        if j.get('name').__eq__(product['name']):
                            j['count'] += i['count']
                edit_excel_data(order['file_name'], file)
                await BaseState.base.set()
                user = get_one_user(data['user_id'])
                data['role'] = user['role']
                await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                    reply_markup=base_menu(data['lang'], data['role']))
                return
            text = translate(data['lang'], 'ORDER_EXCEL_NOT_FOUND')
            await BaseState.base.set()
            user = get_one_user(data['user_id'])
            data['role'] = user['role']
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=base_menu(data['lang'], data['role']))
            return
        text = translate(data['lang'], 'ORDER_EXCEL_NOT_FOUND')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=base_menu(data['lang'], data['role']))
