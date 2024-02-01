from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import latin, russian
from api.orders import order_get_one_order, order_update, order_delete, order_update_office_manager
from api.product import get_products, get_one_product, update_product
from api.users import district_retrieve
from api.users.users import get_one_user, get_office_managers
from button.inline import order_all_inline, choice_order_type, choice_order_params, order_product_all, check_basket, \
    order_update_all_inline, get_all_not_order_agent
from button.reply_markup import bron_menu, back_menu, send_update_menu, base_menu, bron_confirmed_or_unconfirmed_menu
from dispatch import dp
from states.bron import BronState, UpdateBronState, OrderUpdateState, GetAllBronState
from utils.number_split_for_price import price_split


@dp.message_handler(lambda message: (str(message.text).__eq__(russian['UPDATE_ORDER']) or str(message.text).__eq__(
    latin['UPDATE_ORDER']) or str(message.text).__eq__(translate_cyrillic_or_latin(latin['UPDATE_ORDER'], 'cyr'))) and (
                                            not str(message.text).__eq__('/start')),
                    state=GetAllBronState.begin)
async def update_order_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['page'] = 1
        text = translate(data['lang'], 'CHOICE_UPDATE_ORDER')
        text1 = translate(data['lang'], 'CHOICE_ORDER')
        await UpdateBronState.orders.set()
        orders = get_all_not_order_agent(token=data['token'])
        if orders:
            await UpdateBronState.orders.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
            await message.bot.send_message(text=text1, chat_id=message.chat.id, reply_markup=orders)
        else:
            text = translate(data['lang'], 'NOT_FOUND')
            await GetAllBronState.begin.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=bron_confirmed_or_unconfirmed_menu(data['lang']))


@dp.callback_query_handler(state=UpdateBronState.orders)
async def update_order_name_home_handler(call: types.CallbackQuery, state: FSMContext):
    props = call.data
    await call.message.delete()
    async with state.proxy() as data:
        if props.__eq__("exit"):
            text = translate(data['lang'], 'BACK')
            await GetAllBronState.begin.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=bron_menu(data['lang']))
            return
        if props.__eq__("next"):
            data['page'] += 1
            text = translate(data['lang'], 'CHOICE_UPDATE_ORDER')
            await UpdateBronState.orders.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=order_update_all_inline(page=data['page'],
                                                                                     token=data['token'],
                                                                                     lang=data['lang']))
            return
        if props.__eq__("prev"):
            data['page'] += 1
            text = translate(data['lang'], 'CHOICE_UPDATE_ORDER')
            await UpdateBronState.orders.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=order_update_all_inline(page=data['page'],
                                                                                     token=data['token'],
                                                                                     lang=data['lang']))
            return
        data['order_id'] = props[1:]
        order_one = order_get_one_order(order_id=data['order_id'], token=data['token'])
        seller = get_one_user(order_one['seller'])
        name = f"{seller['first_name']}"
        if seller['last_name']:
            name = f"{seller['first_name']} {seller['last_name']}"
        text = f"{translate(data['lang'], 'COMPANY_NAME')}:{order_one.get('company_name')}\n{translate(data['lang'], 'INN_GET')}: {order_one.get('inn')}\n{translate(data['lang'], 'COMMENT_GET')}:{order_one.get('comment')}\n{translate(data['lang'], 'CREATOR')}: {translate_cyrillic_or_latin(name, data['lang'])}\n\n"
        for i, product in enumerate(order_one.get("products"), start=1):
            product_one = get_one_product(product_id=product.get("product"), token=data['token'])
            text += f"{i}){translate(data['lang'], 'NAME')}:{product_one.get('name')}\n{translate(data['lang'], 'COUNT')}:{product['count']}\n{translate(data['lang'], 'PRICE')}({order_one.get('type_price')}):{price_split(product.get('price'))} {translate(data['lang'], 'SUM')}\n"
        text += f"\n{translate(data['lang'], 'CREATED_DATE')}:{order_one['created_date']}\n{translate(data['lang'], 'TOTAL_PRICE')}({order_one.get('type_price')}):{price_split(order_one.get('total_price'))} {translate(data['lang'], 'SUM')}"
        await UpdateBronState.update.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=send_update_menu(data['lang']))


@dp.message_handler(lambda message: (str(message.text).__eq__(latin['SEND_OFFICE_MANAGER']) or str(message.text).__eq__(
    russian['SEND_OFFICE_MANAGER']) or str(message.text).__eq__(
    translate_cyrillic_or_latin(latin['SEND_OFFICE_MANAGER'], 'cyr'))) and (
                                            not str(message.text).__eq__('/start')), state=UpdateBronState.update)
async def send_office_manager_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'IS_SEND_OFFICE_MANAGER')
        await UpdateBronState.check.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=check_basket(data['lang']))


@dp.callback_query_handler(state=UpdateBronState.check)
async def check_send_office_manager_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data.__eq__("no"):
            order_one = order_get_one_order(order_id=data['order_id'], token=data['token'])
            seller = get_one_user(order_one['seller'])
            name = f"{seller['first_name']}"
            if seller['last_name']:
                name = f"{seller['first_name']} {seller['last_name']}"
            text = f"{translate(data['lang'], 'COMPANY_NAME')}:{order_one.get('company_name')}\n{translate(data['lang'], 'INN_GET')}: {order_one.get('inn')}\n{translate(data['lang'], 'COMMENT_GET')}:{order_one.get('comment')}\n{translate(data['lang'], 'CREATOR')}: {translate_cyrillic_or_latin(name, data['lang'])}\n\n"
            for i, product in enumerate(order_one.get("products"), start=1):
                product_one = get_one_product(product_id=product.get("product"), token=data['token'])
                text += f"{i}){translate(data['lang'], 'NAME')}:{product_one.get('name')}\n{translate(data['lang'], 'COUNT')}: {product['count']}\n{translate(data['lang'], 'PRICE')}({order_one.get('type_price')}):{price_split(product.get('price'))} {translate(data['lang'], 'SUM')}\n\n"
            text += f"\n{translate(data['lang'], 'CREATED_DATE')}:{order_one['created_date']}\n{translate(data['lang'], 'TOTAL_PRICE')}({order_one.get('type_price')}):{price_split(order_one.get('total_price'))} {translate(data['lang'], 'SUM')}"
            await UpdateBronState.update.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=send_update_menu(data['lang']))
            return
        managers = get_office_managers()
        user = get_one_user(data['user_id'])
        district = district_retrieve(user['district'])
        name = user['first_name']
        order_one = order_get_one_order(order_id=data['order_id'], token=data['token'])
        if user['last_name']:
            name = f"{user['first_name']} {user['last_name']}"
        for manager in managers:
            text2 = f"{translate(data['lang'], 'COMPANY_NAME')}: {data['companyName']}\nInn: {data['order_inn']}\n{translate(data['lang'], 'CREATOR')}: {name}\n{translate(data['lang'], 'DISTRICT')}: {translate_cyrillic_or_latin(district['name'], data['lang'])}\n\t\t\t\t\t\t{translate(data['lang'], 'BASKET')}\n"
            for i, product in enumerate(order_one.get("products"), start=1):
                product_one = get_one_product(product_id=product.get("product"), token=data['token'])
                text2 += f"{i}){translate(data['lang'], 'NAME')}:{product_one.get('name')}\n{translate(data['lang'], 'COUNT')}: {product['count']}\n{translate(data['lang'], 'PRICE')}({order_one.get('type_price')}):{price_split(product.get('price'))} {translate(data['lang'], 'SUM')}\n\n"
            text2 += f"\n{translate(data['lang'], 'CREATED_DATE')}:{order_one['created_date']}\n{translate(data['lang'], 'TOTAL_PRICE')}({order_one.get('type_price')}):{price_split(order_one.get('total_price'))} {translate(data['lang'], 'SUM')}"
            await call.message.bot.send_message(text=text2, chat_id=manager['chat_id'])
        text1 = translate(data['lang'], 'SUCCESS_SEND')
        order = order_get_one_order(token=data['token'], order_id=data['order_id'])
        products = order['products']
        total_price = order['total_price']
        type_price = order['type_price']
        seller = order['seller']
        order_id = order['id']
        inn = order['inn']
        token = data['token']
        comment = order['comment']
        order_update_office_manager(products=products,
                                    order_id=order_id,
                                    inn=inn,
                                    comment=comment,
                                    total_price=total_price,
                                    type_price=type_price,
                                    token=token,
                                    seller=seller,
                                    is_manager_send=True)
        await GetAllBronState.begin.set()
        await call.message.bot.send_message(text=text1, chat_id=call.message.chat.id,
                                            reply_markup=bron_confirmed_or_unconfirmed_menu(data['lang']))


@dp.message_handler(lambda message: (str(message.text).__eq__(russian['DELETE_ORDER']) or str(message.text).__eq__(
    latin['DELETE_ORDER']) or str(message.text).__eq__(translate_cyrillic_or_latin(latin['DELETE_ORDER'], 'cyr'))) and (
                                            not str(message.text).__eq__('/start')),
                    state=UpdateBronState.update)
async def delete_order_send(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'IS_DELETED')
        await UpdateBronState.delete.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=check_basket(data['lang']))


@dp.callback_query_handler(state=UpdateBronState.delete)
async def delete_order_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data.__eq__("no"):
            order_one = order_get_one_order(order_id=data['order_id'], token=data['token'])
            seller = get_one_user(order_one['seller'])
            name = f"{seller['first_name']}"
            if seller['last_name']:
                name = f"{seller['first_name']} {seller['last_name']}"
            text = f"{translate(data['lang'], 'COMPANY_NAME')}:{order_one.get('company_name')}\n{translate(data['lang'], 'INN_GET')}: {order_one.get('inn')}\n{translate(data['lang'], 'COMMENT_GET')}:{order_one.get('comment')}\n{translate(data['lang'], 'CREATOR')}: {translate_cyrillic_or_latin(name, data['lang'])}\n\n"
            for i, product in enumerate(order_one.get("products")):
                product_one = get_one_product(product_id=product.get("product"), token=data['token'])
                text += f"{i}){translate(data['lang'], 'NAME')}:{product_one.get('name')}\n{translate(data['lang'], 'PRICE')}({order_one.get('type_price')}):{price_split(product.get('price'))} {translate(data['lang'], 'SUM')}\n"
            text += f"\n{translate(data['lang'], 'CREATED_DATE')}:{str(order_one['created_date'][:10]) + ' ' + order_one['created_date'][11:16]}\n{translate(data['lang'], 'TOTAL_PRICE')}({order_one.get('type_price')}):{price_split(order_one.get('total_price'))} {translate(data['lang'], 'SUM')}"
            await UpdateBronState.update.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=send_update_menu(data['lang']))
            return
        order_delete(order_id=data['order_id'], token=data['token'])
        text1 = translate(data['lang'], 'SUCCESS_DELETED')
        # text = translate(data['lang'], 'BASE_MENU_BACK')
        await BronState.bron.set()
        await call.message.bot.send_message(text=text1, chat_id=call.message.chat.id,
                                            reply_markup=bron_menu(data['lang']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[UpdateBronState.inn, UpdateBronState.comment, UpdateBronState.type_update,
           UpdateBronState.update, UpdateBronState.orders, UpdateBronState.orders, ])
async def back_menu_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'BASE_MENU_BACK')
        await BronState.bron.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=bron_menu(data['lang']))
