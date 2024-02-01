from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import russian, latin
from api.orders.company import Company
from api.users.users import get_one_user
from button.inline import company_all_inline, check_basket
from button.reply_markup import base_menu, back_menu
from dispatch import dp
from states import CreateCompanyBossesState, BaseState, HospitalResidueState


@dp.message_handler(state=CreateCompanyBossesState.director_name)
async def create_director_name_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                data['director_name'] = message.text
                text = translate(data['lang'], 'CREATE_DIRECTOR_PHONE_NUMBER')
                await CreateCompanyBossesState.director_phone.set()
                await message.bot.send_message(text=text, chat_id=message.chat.id)
                return
            text = translate(data['lang'], 'CHOICE_COMPANY')
            await HospitalResidueState.begin.set()
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


@dp.message_handler(state=CreateCompanyBossesState.director_phone)
async def create_director_phone_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                data['director_phone'] = message.text
                text = translate(data['lang'], 'CREATE_PROVIDER_NAME')
                await CreateCompanyBossesState.provider_name.set()
                await message.bot.send_message(text=text, chat_id=message.chat.id)
                return
            text = translate(data['lang'], 'CREATE_DIRECTOR_NAME')
            await CreateCompanyBossesState.director_name.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id)
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(state=CreateCompanyBossesState.provider_name)
async def create_provider_name_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                data['provider_name'] = message.text
                text = translate(data['lang'], 'CREATE_PROVIDER_PHONE_NUMBER')
                await CreateCompanyBossesState.provider_phone.set()
                await message.bot.send_message(text=text, chat_id=message.chat.id)
                return
            text = translate(data['lang'], 'CREATE_DIRECTOR_PHONE_NUMBER')
            await CreateCompanyBossesState.director_phone.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id)
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(state=CreateCompanyBossesState.provider_phone)
async def create_provider_phone_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                data['provider_phone'] = message.text
                text = f"{translate(data['lang'], 'DIRECTOR_NAME')}: {data['director_name']}\n{translate(data['lang'], 'DIRECTOR_PHONE_NUMBER')}:{data['director_phone']}\n{translate(data['lang'], 'PROVIDER_NAME')}:{data['provider_name']}\n{translate(data['lang'], 'PROVIDER_PHONE_NUMBER')}:{data['provider_phone']}\n{translate(data['lang'], 'CHECK_CREATE_BOSSES')}"
                await CreateCompanyBossesState.check.set()
                await message.bot.send_message(text=text, chat_id=message.chat.id,
                                               reply_markup=check_basket(data['lang']))
                return
            text = translate(data['lang'], 'CREATE_PROVIDER_NAME')
            await CreateCompanyBossesState.provider_name.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id)
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.callback_query_handler(state=CreateCompanyBossesState.check)
async def check_bosses_data_handler(call: types.CallbackQuery, state: FSMContext):
    props = call.data
    async with state.proxy() as data:
        if props.__eq__("no"):
            data['page'] = 1
            data['search'] = None
            text = f"{translate(data['lang'], 'CANCEL_BOSSES_UPDATED')}\n{translate(data['lang'], 'CHOICE_COMPANY')}"
            text2 = translate(data['lang'], 'OR_SEARCH')
            await HospitalResidueState.begin.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=back_menu(data['lang']))
            await call.message.bot.send_message(text=text2, chat_id=call.message.chat.id,
                                                reply_markup=company_all_inline(data['page'], data['search'],
                                                                                data['token'],
                                                                                data['lang']))
        if props.__eq__("yes"):
            Company(provider_name=data['provider_name'], provider_phone=data['provider_phone'],
                    director_phone=data['director_phone'], director_name=data['director_name'],
                    company_id=data['company_id'], token=data['token']).update()
            data['page'] = 1
            data['search'] = None
            text = f"{translate(data['lang'], 'SUCCESS_BOSSES_UPDATED')}\n{translate(data['lang'], 'CHOICE_COMPANY')}"
            text2 = translate(data['lang'], 'OR_SEARCH')
            await HospitalResidueState.begin.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=back_menu(data['lang']))
            await call.message.bot.send_message(text=text2, chat_id=call.message.chat.id,
                                                reply_markup=company_all_inline(data['page'], data['search'],
                                                                                data['token'],
                                                                                data['lang']))
