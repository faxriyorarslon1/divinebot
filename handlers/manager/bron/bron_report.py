from os.path import join

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import latin, russian
from api.users.excel_for_order import OrderExcel
from api.users.users import get_one_user
from button.inline import months, get_month_day
from button.reply_markup import base_menu, back_menu, bron_report_menu, office_manager_orders
from dispatch import dp
from excel_utils import check_excel
from excel_utils.product_report import PRODUCT_EXCEL_PATH
from states import BaseState
from states.bron import BronReportState
from states.orders import WarehouseState


@dp.message_handler(lambda message: (str(message.text).__eq__(latin["BRON_REPORT"]) or str(message.text).__eq__(
    russian["BRON_REPORT"]) or str(message.text).__eq__(translate_cyrillic_or_latin(latin["BRON_REPORT"], 'cyr'))) and (
                                            not str(message.text).__eq__('/start')),
                    state=BaseState.base)
async def bron_menu_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text2 = translate(data['lang'], 'CHOICE_VIZIT')
        await BronReportState.begin.set()
        await message.bot.send_message(text=text2, chat_id=message.chat.id, reply_markup=bron_report_menu(data['lang']))


@dp.message_handler(lambda message: (str(message.text).__eq__(latin["EXCEL_FORMAT"]) or str(message.text).__eq__(
    russian["EXCEL_FORMAT"]) or str(message.text).__eq__(
    translate_cyrillic_or_latin(latin["EXCEL_FORMAT"], 'cyr'))) and (not str(message.text).__eq__('/start')),
                    state=BronReportState.begin)
async def bron_report_begin_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        order = OrderExcel(token=data['token']).get_excel()
        file = check_excel(PRODUCT_EXCEL_PATH, order['file_name'])
        if order:
            if file.startswith("bos"):
                await BaseState.base.set()
                user = get_one_user(data['user_id'])
                data['role'] = user['role']
                await message.bot.send_document(document=open(join(PRODUCT_EXCEL_PATH, order['file_name']), 'rb+'),
                                                chat_id=message.chat.id)
            else:
                text = translate(data['lang'], 'ORDER_EXCEL_NOT_FOUND')
                await BaseState.base.set()
                user = get_one_user(data['user_id'])
                data['role'] = user['role']
                await message.bot.send_message(text=text, chat_id=message.chat.id,
                                               reply_markup=base_menu(data['lang'], data['role']))
        else:
            text = translate(data['lang'], 'ORDER_EXCEL_NOT_FOUND')
            await BaseState.base.set()
            user = get_one_user(data['user_id'])
            data['role'] = user['role']
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(lambda message: (str(message.text).__eq__(latin["TEXT_FORMAT"]) or str(message.text).__eq__(
    russian["TEXT_FORMAT"]) or str(message.text).__eq__(translate_cyrillic_or_latin(latin["TEXT_FORMAT"], 'cyr'))) and (
                                            not str(message.text).__eq__('/start')),
                    state=BronReportState.begin)
async def debit_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'WAREHOUSE_MENU')
        text2 = translate(data['lang'], 'OR_THE_BACK')
        await BronReportState.one.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
        await message.bot.send_message(text=text2, chat_id=message.chat.id, reply_markup=months(data['lang']))


@dp.callback_query_handler(state=BronReportState.one)
async def cal_data_for_warehouse_menu_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['month'] = call.data[1:]
        text = translate(data['lang'], 'MONTHS_CHOICE')
        await BronReportState.month.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=get_month_day(data['month']))


@dp.callback_query_handler(state=BronReportState.month)
async def cal_data_month_day_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['day'] = call.data[1:]
        text = translate(data['lang'], 'DAY')
        await WarehouseState.day.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=office_manager_orders(data['lang']))


@dp.message_handler(lambda message: (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
    russian['BACK_MENU']) or message.text.__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                                            not str(message.text).__eq__('/start')),
                    state=[BronReportState.begin, BronReportState.month])
async def settings_back_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(lang=data['lang'], text='BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))
