from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import latin, russian
from api.orders import get_not_agent_confirmed_orders, order_get_one_order, order_update
from api.product import get_one_product
from api.users.users import get_one_user
from button.inline import get_all_order_agent, get_all_not_order_agent, check_basket, order_update_all_inline
from button.reply_markup import bron_confirmed_or_unconfirmed_menu, back_menu, bron_menu
from dispatch import dp
from states.bron import GetAllBronState, BronState, UpdateBronState
from utils.number_split_for_price import price_split


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['UNCONFIRMED_AGENT_ORDERS']) or str(message.text).__eq__(
        russian['UNCONFIRMED_AGENT_ORDERS']) or str(message.text).__eq__(
        translate_cyrillic_or_latin(latin['UNCONFIRMED_AGENT_ORDERS'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')), state=GetAllBronState.begin)
async def not_confirmed_agent_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'NOT_CONFIRMED_TEXT')
        text2 = translate(data['lang'], 'OR_THE_BACK')
        orders = get_all_not_order_agent(token=data['token'])
        if orders:
            await UpdateBronState.orders.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
            await message.bot.send_message(text=text2, chat_id=message.chat.id, reply_markup=orders)
            return
        text = translate(data['lang'], 'NOT_FOUND')
        await GetAllBronState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=bron_confirmed_or_unconfirmed_menu(data['lang']))


@dp.callback_query_handler(state=GetAllBronState.not_confirmed)
async def not_confirmed_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['order_id'] = call.data[1:]
        order_one = order_get_one_order(order_id=data['order_id'], token=data['token'])
        seller = get_one_user(order_one['seller'])
        name = f"{seller['first_name']}"
        if seller['last_name']:
            name = f"{seller['first_name']} {seller['last_name']}"
        text = f"{translate(data['lang'], 'COMPANY_NAME')}:{order_one.get('company_name')}\n{translate(data['lang'], 'INN_GET')}: {order_one.get('inn')}\n{translate(data['lang'], 'COMMENT_GET')}:{order_one.get('comment')}\n{translate(data['lang'], 'CREATOR')}: {translate_cyrillic_or_latin(name, data['lang'])}\n\n"
        for i, product in enumerate(order_one.get("products"), start=1):
            product_one = get_one_product(product_id=product.get("product"), token=data['token'])
            text += f"{i}){translate(data['lang'], 'NAME')}:{product_one.get('name')}\n{translate(data['lang'], 'PRICE')}({order_one.get('type_price')}):{price_split(product.get('price'))} {translate(data['lang'], 'SUM')}\n\n"
        text += f"\n{translate(data['lang'], 'CREATED_DATE')}:{order_one['created_date']}\n{translate(data['lang'], 'TOTAL_PRICE')}({order_one.get('type_price')}):{price_split(order_one.get('total_price'))} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'STATUS')} : {translate_cyrillic_or_latin('Menedjer', data['lang'])}\n"
        text += translate(data['lang'], 'IS_SEND_OFFICE_MANAGER')
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=check_basket(data['lang']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=GetAllBronState.check)
async def back_menu_agent_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'BACK')
        await GetAllBronState.not_confirmed.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=get_all_not_order_agent(token=data['token']))


@dp.callback_query_handler(state=GetAllBronState.check)
async def check_send_office_manager_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data.__eq__("no"):
            order_one = order_get_one_order(order_id=data['order_id'], token=data['token'])
            text = f"{translate(data['lang'], 'COMPANY_NAME')}:{order_one.get('company_name')}\n{translate(data['lang'], 'INN_GET')}{order_one.get('inn')}\n{translate(data['lang'], 'COMMENT_GET')}:{order_one.get('comment')}\n\n"
            for i, product in enumerate(order_one.get("products"), start=1):
                product_one = get_one_product(product_id=product.get("product"), token=data['token'])
                text += f"{i}){translate(data['lang'], 'NAME')}:{product_one.get('name')}\n{translate(data['lang'], 'PRICE')}({order_one.get('type_price')}):{price_split(product.get('price'))} {translate(data['lang'], 'SUM')}\n\n"
            text += f"\n{translate(data['lang'], 'CREATED_DATE')}:{str(order_one['created_date'][:10]) + ' ' + order_one['created_date'][11:16]}\n{translate(data['lang'], 'TOTAL_PRICE')}({order_one.get('type_price')}):{price_split(order_one.get('total_price'))} {translate(data['lang'], 'SUM')}"
            orders = get_all_not_order_agent(token=data['token'])
            if orders:
                await GetAllBronState.not_confirmed.set()
                await call.message.bot.send_message(text=text, chat_id=call.message.chat.id, reply_markup=orders)
                return
            text = translate(data['lang'], 'NOT_FOUND')
            await GetAllBronState.begin.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=bron_confirmed_or_unconfirmed_menu(data['lang']))
            return
        order = order_get_one_order(token=data['token'], order_id=data['order_id'])
        products = order['products']
        total_price = order['total_price']
        type_price = order['type_price']
        seller = order['seller']
        order_id = order['id']
        inn = order['inn']
        token = data['token']
        comment = order['comment']
        order_update(products=products, order_id=order_id, inn=inn, comment=comment, total_price=total_price,
                     type_price=type_price, token=token, seller=seller, is_manager_send=True)
        text = translate(data['lang'], 'CHOICE_UPDATE_ORDER')
        orders = get_all_not_order_agent(token=data['token'])
        if orders:
            await GetAllBronState.not_confirmed.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id, reply_markup=orders)
            return
        text = translate(data['lang'], 'NOT_FOUND')
        await GetAllBronState.begin.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=bron_confirmed_or_unconfirmed_menu(data['lang']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=GetAllBronState.not_confirmed)
async def back_menu_agent_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'BACK')
        await GetAllBronState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=bron_confirmed_or_unconfirmed_menu(data['lang']))
