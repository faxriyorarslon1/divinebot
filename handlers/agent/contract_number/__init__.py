from datetime import datetime

from api.users import district_retrieve
from excel_utils.user.contract_number import create_contract_excel, write_contract_number_agent
from utils.contract_number_json import write_contract_number
from .get_contract_number import *
from aiogram import types
from aiogram.dispatcher import FSMContext
from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import latin, russian
from api.orders import set_order_contract_number, update_new_contract_number, order_get_one_order
from api.users.users import get_one_user
from button.inline import check_basket
from button.reply_markup import contract_number_menu, base_menu, back_menu
from dispatch import dp
from states import BaseState, ContractNumberState


@dp.message_handler(
    lambda message: str(message.text).__eq__(latin['DOGOVOR']) or str(message.text).__eq__(russian['DOGOVOR']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['DOGOVOR'], 'cyr')), state=BaseState.base)
async def contract_menu_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'CONTRACT_NUMBER_MENU')
        await ContractNumberState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=contract_number_menu(data['lang']))


@dp.message_handler(lambda message: message.text.__eq__(latin["BACK_MENU"]) or message.text.__eq__(
    russian["BACK_MENU"]) or message.text.__eq__(
    translate_cyrillic_or_latin(latin["BACK_MENU"], 'cyr')),
                    state=[ContractNumberState.begin, ContractNumberState.set_inn,
                           ContractNumberState.get_contract_number, ContractNumberState.company_name])
async def back_contract_number_page_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(lambda message: str(message.text).__eq__(latin['BUY_CONTRACT_NUMBER']) or str(message.text).__eq__(
    russian['BUY_CONTRACT_NUMBER']) or str(message.text).__eq__(
    translate_cyrillic_or_latin(latin['BUY_CONTRACT_NUMBER'], 'cyr')), state=ContractNumberState.begin)
async def get_contract_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'SET_INN')
        await ContractNumberState.set_inn.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=ContractNumberState.set_inn)
async def get_contract_number_function(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        contract_number = set_order_contract_number(message.text, data['token'])
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not message.text.__eq__(latin["BACK_MENU"]) or message.text.__eq__(
                    russian["BACK_MENU"]) or message.text.__eq__(
                translate_cyrillic_or_latin(latin["BACK_MENU"], 'cyr')):
                if contract_number.get('id'):
                    data['contract_id'] = contract_number['id']
                    text = f"{translate(data['lang'], 'COMPANY_NAME')}:{translate_cyrillic_or_latin(contract_number['company_name'], data['lang'])}\n{translate(data['lang'], 'CURRENT_COMPANY_CHOICE_CONTRACT_NUMBER')}"
                    await ContractNumberState.company_name.set()
                    await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=check_basket())
                    return
                text = translate(data['lang'], 'ERROR_INN')
                await ContractNumberState.set_inn.set()
                await message.bot.send_message(text=text, chat_id=message.chat.id)
                return
            text = translate(data['lang'], 'BACK')
            await BaseState.base.set()
            user = get_one_user(data['user_id'])
            data['role'] = user['role']
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=base_menu(data['lang'], data['role']))
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.callback_query_handler(state=ContractNumberState.company_name)
async def new_contract_number_create(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data.__eq__('yes'):
            text = translate(data['lang'], 'UPDATE_CONTRACT_NUMBER')
            update = update_new_contract_number(data['contract_id'], data['token'])
            order_one = order_get_one_order(data['contract_id'], data['token'])
            user = get_one_user(order_one['seller'])
            village = district_retrieve(user['district'])
            date_year = datetime.now().year
            date_month = datetime.now().month
            date_day = datetime.now().day
            time = f"{date_day}.{date_month}.{date_year}"
            last_name = None
            if user['last_name']:
                last_name = user['last_name']
            write_contract_number_agent(update['contract_number'], time, update['company_name'], update['inn'],
                                        user['phone_number'], village['name'], user['first_name'], last_name,
                                        token=data['token'])
            text += f"{translate(data['lang'], 'COMPANY_NAME')}:{translate_cyrillic_or_latin(update['company_name'], data['lang'])}\n{translate(data['lang'], 'INN')}:{translate_cyrillic_or_latin(update['inn'], data['lang'])}\n{translate(data['lang'], 'CONTRACT_NUMBER_CREATED_AT')}:{update['create_contract_number'][:10]} {update['create_contract_number'][11:16]}\n{translate(data['lang'], 'CONTRACT_NUMBER')}:{update['contract_number']}"
            await BaseState.base.set()
            user = get_one_user(data['user_id'])
            data['role'] = user['role']
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=base_menu(data['lang'], data['role']))
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=base_menu(data['lang'], data['role']))
