from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import latin, russian
from api.orders import order_get_one_order, update_status
from api.product import get_one_product
from api.users import district_retrieve
from api.users.users import get_one_user
from button.inline import village_all_inline, mp_or_agent, users, user_role_order, get_unreviewed_orders_inline, \
    check_delivery
from button.reply_markup import back_menu, office_manager_orders
from dispatch import dp
from states import WorkerWarehouseState
from states.orders import WarehouseState
from utils.number_split_for_price import price_split


@dp.message_handler(lambda message: (str(message.text).__eq__(latin['BY_WORKERS']) or str(message.text).__eq__(
    russian['BY_WORKERS']) or str(message.text).__eq__(translate_cyrillic_or_latin(latin['BY_WORKERS'], 'cyr'))) and (
                                            not str(message.text).__eq__('/start')),
                    state=WarehouseState.day)
async def village_order_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'CREATE_VILLAGE')
        text2 = translate(data['lang'], 'OR_THE_BACK')
        await WorkerWarehouseState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
        await message.bot.send_message(text=text2, chat_id=message.chat.id,
                                       reply_markup=village_all_inline(data['lang']))


@dp.message_handler(lambda message: (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
    russian['BACK_MENU']) or message.text.__eq__(
    translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (not str(message.text).__eq__('/start')),
                    state=WorkerWarehouseState.begin)
async def back_handler_office_manager(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'DAY')
        await WarehouseState.day.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=office_manager_orders(data['lang']))


@dp.callback_query_handler(state=WorkerWarehouseState.begin)
async def cal_district_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['village'] = call.data[1:]
        order = mp_or_agent(data['lang'])
        if order:
            text = translate(data['lang'], 'CHOICE_ORDER')
            await WorkerWarehouseState.finish.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id, reply_markup=order)
            return
        text2 = translate(data['lang'], 'NOT_FOUND')
        await call.message.delete()
        await WorkerWarehouseState.begin.set()
        await call.message.bot.send_message(text=text2, chat_id=call.message.chat.id,
                                            reply_markup=village_all_inline(data['lang']))


@dp.message_handler(lambda message: (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
    russian['BACK_MENU']) or message.text.__eq__(
    translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (not str(message.text).__eq__('/start')),
                    state=WorkerWarehouseState.finish)
async def back_handler_office_manager(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text2 = translate(data['lang'], 'BACK')
        await message.delete()
        await WorkerWarehouseState.begin.set()
        await message.bot.send_message(text=text2, chat_id=message.chat.id,
                                       reply_markup=village_all_inline(data['lang']))


@dp.callback_query_handler(state=WorkerWarehouseState.finish)
async def cal_worker_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['user_role'] = call.data
        worker = users(role=data['user_role'], district=data['village'], token=data['token'], lang=data['lang'])
        if worker:
            text = translate(data['lang'], 'CHOICE_ORDER')
            await WorkerWarehouseState.worker.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id, reply_markup=worker)
            return
        text = translate(data['lang'], 'NOT_FOUND')
        await WorkerWarehouseState.finish.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=mp_or_agent(data['lang']))


@dp.message_handler(lambda message: (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
    russian['BACK_MENU']) or message.text.__eq__(
    translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (not str(message.text).__eq__('/start')),
                    state=WorkerWarehouseState.worker)
async def back_handler_office_manager(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text2 = translate(data['lang'], 'BACK')
        await message.delete()
        await WorkerWarehouseState.begin.set()
        await message.bot.send_message(text=text2, chat_id=message.chat.id,
                                       reply_markup=village_all_inline(data['lang']))


@dp.callback_query_handler(state=WorkerWarehouseState.worker)
async def worker_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data.__eq__('back'):
            text = translate(data['lang'], 'BACK')
            await WorkerWarehouseState.finish.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=mp_or_agent(data['lang']))
        else:
            data['success_user'] = call.data[1:]
            data['order_user_id'] = call.data
            text = translate(data['lang'], 'CHOICE_ORDER')
            user = user_role_order(user_id=call.data[1:], day=data['day'],
                                   month=data['month'], token=data['token'],
                                   lang=data['lang'])
            if user:
                await WorkerWarehouseState.order_worker.set()
                await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                    reply_markup=user)
                return
            text = translate(data['lang'], 'NOT_FOUND')
            await WorkerWarehouseState.finish.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=mp_or_agent(data['lang']))


@dp.message_handler(lambda message: (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
    russian['BACK_MENU']) or message.text.__eq__(
    translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (not str(message.text).__eq__('/start')),
                    state=WorkerWarehouseState.order_worker)
async def back_handler_office_manager(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'BACK')
        await WorkerWarehouseState.worker.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=users(role=data['user_role'], district=data['village'],
                                                          token=data['token'], lang=data['lang']))


@dp.callback_query_handler(state=WorkerWarehouseState.order_worker)
async def final_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data.__eq__('back'):
            text = translate(data['lang'], 'CHOICE_ORDER')
            await WorkerWarehouseState.worker.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=users(role=data['user_role'], district=data['village'],
                                                                   token=data['token'], lang=data['lang']))
        else:
            data['order_id'] = call.data[1:]
            order_one = order_get_one_order(order_id=data['order_id'], token=data['token'])
            is_manager_send = ""
            status = order_one['status']
            if status.__eq__('office_manager'):
                status = translate_cyrillic_or_latin("Offis Menedjer", data['lang'])
            elif status.__eq__('delivery'):
                status = translate_cyrillic_or_latin("Yetkazib beruvchida", data['lang'])
            elif status.__eq__('supplier'):
                status = translate_cyrillic_or_latin("Omborxonada", data['lang'])
            elif status.__eq__('manager'):
                status = translate_cyrillic_or_latin('MP/Menedjerda', data['lang'])
            user = get_one_user(order_one['seller'])
            district = district_retrieve(user['district'])
            name = user['first_name']
            if user['last_name']:
                name = f"{user['first_name']} {user['last_name']}"
            text = f"{translate(data['lang'], 'COMPANY_NAME')}: {order_one['company_name']}\nInn: {order_one['inn']}\n{translate_cyrillic_or_latin('Status', data['lang'])}: {status}\n{translate(data['lang'], 'CREATOR')}: {name}\n{translate(data['lang'], 'DISTRICT')}: {translate_cyrillic_or_latin(district['name'], data['lang'])}\n\t\t\t\t\t\t{translate(data['lang'], 'BASKET')}\n"
            for i, product in enumerate(order_one.get("products"), start=1):
                product_one = get_one_product(product_id=product.get("product"), token=data['token'])
                text += f"{i}){translate(data['lang'], 'NAME')}:{product_one.get('name')}\n{translate(data['lang'], 'COUNT')}:{price_split(product.get('count'))}\n{translate(data['lang'], 'PRICE')}({order_one.get('type_price')}):{price_split(product.get('price'))} {translate(data['lang'], 'SUM')}\n\n"
            text += f"\n{translate(data['lang'], 'CREATED_DATE')}:{str(order_one['created_date'][:10]) + ' ' + order_one['created_date'][11:16]}\n{translate(data['lang'], 'TOTAL_PRICE')}({order_one.get('type_price')}):{price_split(order_one.get('total_price'))} {translate(data['lang'], 'SUM')}"
            if order_one['status'].__eq__('office_manager'):
                await WorkerWarehouseState.check.set()
                await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                    reply_markup=check_delivery(data['lang']))
                return
            await WorkerWarehouseState.order_worker.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=user_role_order(user_id=call.data[1:],
                                                                             day=data['day'],
                                                                             month=data['month'],
                                                                             token=data['token'],
                                                                             lang=data['lang']))


@dp.message_handler(lambda message: (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
    russian['BACK_MENU']) or message.text.__eq__(
    translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (not str(message.text).__eq__('/start')),
                    state=WorkerWarehouseState.check)
async def back_handler_office_manager(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'BACK')
        user = user_role_order(user_id=data['success_user'], day=data['day'],
                               month=data['month'], token=data['token'],
                               lang=data['lang'])
        if user:
            await WorkerWarehouseState.order_worker.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=user)
            return
        text = translate(data['lang'], 'NOT_FOUND')
        await WorkerWarehouseState.finish.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=mp_or_agent(data['lang']))


@dp.callback_query_handler(state=WorkerWarehouseState.check)
async def checked_for_send_confirm_for_delivery(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'SUCCESSFULLY')
        update_status(status='delivery',
                      order_id=data['order_id'],
                      token=data['token'])
        user = user_role_order(user_id=data['success_user'], day=data['day'],
                               month=data['month'], token=data['token'],
                               lang=data['lang'])
        if user:
            await WorkerWarehouseState.order_worker.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=user)
            return
        text = translate(data['lang'], 'NOT_FOUND')
        await WorkerWarehouseState.finish.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=mp_or_agent(data['lang']))
