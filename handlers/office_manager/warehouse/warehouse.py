from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import latin, russian
from api.users.users import get_one_user
from button.inline import months, get_month_day
from button.reply_markup import back_menu, base_menu, office_manager_orders
from dispatch import dp
from states import BaseState
from states.orders import WarehouseState


@dp.message_handler(lambda message: (str(message.text).__eq__(latin['WAREHOUSE']) or str(message.text).__eq__(
    russian['WAREHOUSE']) or str(message.text).__eq__(translate_cyrillic_or_latin(latin['WAREHOUSE'], 'cyr'))) and (
                                            not str(message.text).__eq__('/start')),
                    state=BaseState.base)
async def debit_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'WAREHOUSE_MENU')
        text2 = translate(data['lang'], 'OR_THE_BACK')
        await WarehouseState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
        await message.bot.send_message(text=text2, chat_id=message.chat.id, reply_markup=months(data['lang']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[WarehouseState.begin])
async def back_the_base_menu_for_warehouse_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.callback_query_handler(state=WarehouseState.begin)
async def cal_data_for_warehouse_menu_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['month'] = call.data[1:]
        text = translate(data['lang'], 'MONTHS_CHOICE')
        await WarehouseState.month.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=get_month_day(data['month']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[WarehouseState.month])
async def back_the_base_menu_for_warehouse_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'BACK')
        await WarehouseState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=months(data['lang']))


@dp.callback_query_handler(state=WarehouseState.month)
async def cal_data_month_day_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['day'] = call.data[1:]
        text = translate(data['lang'], 'DAY')
        await WarehouseState.day.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=office_manager_orders(data['lang']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                    not str(message.text).__eq__('/start')),
    state=[WarehouseState.day])
async def back_the_base_menu_for_warehouse_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'DAY')
        text2 = translate(data['lang'], 'OR_THE_BACK')
        await WarehouseState.month.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
        await message.bot.send_message(text=text2, chat_id=message.chat.id,
                                       reply_markup=get_month_day(data['month']))
