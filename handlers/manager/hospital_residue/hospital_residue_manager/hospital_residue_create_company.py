from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import russian, latin
from api.orders.company import Company
from api.users.users import get_one_user
from button.inline import company_all_inline
from button.reply_markup import back_menu, base_menu
from dispatch import dp
from states import HospitalResidueState, BaseState, HospitalResidueManagerState
from states.bron import CreateCompanyState, CreateCompanyManagerState
from utils import get_company


@dp.message_handler(state=HospitalResidueManagerState.inn)
async def create_company_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                data['order_inn'] = message.text
                company = get_company(message.text)
                if company.get("message"):
                    text = translate(data['lang'], 'BAG_FACTURE')
                    await CreateCompanyManagerState.name.set()
                    await message.bot.send_message(text=text, chat_id=message.chat.id)
                    return
                inn = get_company(message.text)
                if inn['CompanyInn'] is None:
                    text = translate(data['lang'], 'CREATE_COMPANY_INN')
                    await CreateCompanyManagerState.inn.set()
                    await message.bot.send_message(text=text, chat_id=message.chat.id)
                    return
                data['companyName'] = inn['CompanyName']
                data["companyPhone"] = inn['PhoneNumber']
                data['companyAddress'] = inn['CompanyAddress']
                data['companyBank'] = inn['Accounts'][0]['BankName']
                data['order_inn'] = message.text
                await HospitalResidueManagerState.begin.set()
                Company(company_name=data['companyName'], company_address=data['companyAddress'],
                        phone_number=data['companyPhone'], bank_name=data['companyBank'],
                        inn=data['order_inn'], token=data['token'], created_by=data['user_id']).create()
                text = translate(data['lang'], 'CHOICE_COMPANY')
                text2 = translate(data['lang'], 'OR_SEARCH')
                await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
                await message.bot.send_message(text=text2, chat_id=message.chat.id,
                                               reply_markup=company_all_inline(data['page'], data['search'],
                                                                               data['token'],
                                                                               data['lang']))
                return
            text = translate(data['lang'], 'CHOICE_COMPANY')
            await HospitalResidueManagerState.begin.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=company_all_inline(data['page'], data['search'], data['token'],
                                                                           data['lang']))
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=CreateCompanyManagerState.name)
async def create_company_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                data['companyName'] = message.text
                text = translate(data['lang'], 'CREATE_COMPANY_ADDRESS')
                await CreateCompanyManagerState.address.set()
                await message.bot.send_message(text=text, chat_id=message.chat.id)
                return
            text = translate(data['lang'], 'CREATE_INN')
            await CreateCompanyManagerState.inn.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id)
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=CreateCompanyManagerState.address)
async def create_address_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                data['companyAddress'] = message.text
                text = translate(data['lang'], 'CREATE_COMPANY_PHONE_NUMBER')
                await CreateCompanyManagerState.phone_number.set()
                await message.bot.send_message(text=text, chat_id=message.chat.id)
                return
            text = translate(data['lang'], 'BAG_FACTURE')
            await CreateCompanyManagerState.name.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id)
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'),
                    state=CreateCompanyManagerState.phone_number)
async def create_phone_number_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                data['companyPhone'] = message.text
                text = translate(data['lang'], 'CREATE_COMPANY_BANK_NAME')
                await CreateCompanyManagerState.bank_name.set()
                await message.bot.send_message(text=text, chat_id=message.chat.id)
                return
            text = translate(data['lang'], 'CREATE_COMPANY_ADDRESS')
            await CreateCompanyManagerState.address.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id)
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=CreateCompanyManagerState.bank_name)
async def create_bank_name_number_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                data['company_bank_name'] = message.text
                text = translate(data['lang'], 'CHOICE_COMPANY')
                text2 = translate(data['lang'], 'OR_SEARCH')
                await HospitalResidueManagerState.begin.set()
                Company(company_name=data['companyName'], company_address=data['companyAddress'],
                        phone_number=data['companyPhone'], bank_name=data['company_bank_name'],
                        inn=data['order_inn'], token=data['token'], created_by=data['user_id']).create()
                await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
                await message.bot.send_message(text=text2, chat_id=message.chat.id,
                                               reply_markup=company_all_inline(data['page'], data['search'],
                                                                               data['token'],
                                                                               data['lang']))
                return
            text = translate(data['lang'], 'CREATE_COMPANY_PHONE_NUMBER')
            await CreateCompanyManagerState.phone_number.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id)
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))
