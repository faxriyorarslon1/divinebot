from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import latin, russian
from api.orders.income import Income
from api.users import district_retrieve
from api.users.users import get_one_user
from button.inline import months, get_month_day
from button.reply_markup import base_menu, back_menu
from dispatch import dp
from excel_utils.order import get_excel_income
from states import BaseState, ManagerIncomeState
from utils.number_split_for_price import price_split


@dp.message_handler(lambda message: (message.text.__eq__(russian['INCOME_AGENT']) or message.text.__eq__(
    latin['INCOME_AGENT']) or message.text.__eq__(translate_cyrillic_or_latin(latin['INCOME_AGENT'], 'cyr'))) and (
                                            not str(message.text).__eq__('/start')),
                    state=BaseState.base)
async def agent_debit_menu(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'WAREHOUSE_MENU')
        text2 = translate(data['lang'], 'OR_THE_BACK')
        await ManagerIncomeState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
        await message.bot.send_message(text=text2, chat_id=message.chat.id, reply_markup=months(data['lang']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[ManagerIncomeState.begin])
async def back_the_base_menu_for_warehouse_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.callback_query_handler(state=ManagerIncomeState.begin)
async def cal_data_for_warehouse_menu_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['month'] = call.data[1:]
        text = translate(data['lang'], 'MONTHS_CHOICE')
        await ManagerIncomeState.month.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=get_month_day(data['month']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[ManagerIncomeState.month])
async def back_the_base_menu_for_warehouse_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'BACK')
        await ManagerIncomeState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=months(data['lang']))


@dp.callback_query_handler(state=ManagerIncomeState.month)
async def cal_data_month_day_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['day'] = call.data[1:]
        text = translate(data['lang'], 'DAY')
        get_excel_income_file_name = Income(token=data['token'], day=data['day'], month=data['month']).get_excel()
        district = district_retrieve(data['district'])
        user = get_one_user(data['user_id'])
        name = user['first_name']
        if user['last_name']:
            name = f"{user['first_name']}{user['last_name']}"
        if get_excel_income_file_name:
            file = get_excel_income(get_excel_income_file_name['file_name'], all_name=name, village=district['name'])
            if len(file) != 0:
                text = ""
                total = 0
                for i, f in enumerate(file, start=1):
                    total += f['price']
                    text += f"{i})  {translate(data['lang'], 'NAME_MEMBER')}: {translate_cyrillic_or_latin(f['all_name'], data['lang'])}" \
                            f"\n{translate_cyrillic_or_latin('Dorixona Nomi(Korxona Nomi)', data['lang'])}:  {translate_cyrillic_or_latin(f['company_name'], data['lang'])}" \
                            f"\n{translate_cyrillic_or_latin('Tushum summasi', data['lang'])}: {price_split(f['price'])} {translate(data['lang'], 'SUM')}\n\n"
                text += f"{translate(data['lang'], 'TOTAL_PRICE')}: {price_split(total)} {translate(data['lang'], 'SUM')}"
                await ManagerIncomeState.month.set()
                await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                    reply_markup=get_month_day(data['month']))
                return
            text = translate(data['lang'], 'NOT_FOUND')
            await ManagerIncomeState.month.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=get_month_day(data['month']))
            return
        text = translate(data['lang'], 'NOT_FOUND')
        await ManagerIncomeState.month.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=get_month_day(data['month']))
