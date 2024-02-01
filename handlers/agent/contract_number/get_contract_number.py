from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import latin, russian
from api.orders import get_order_contract_number
from api.users.users import get_one_user
from button.reply_markup import back_menu, base_menu
from dispatch import dp
from excel_utils.user.contract_number import get_contract_number
from states import ContractNumberState, BaseState


@dp.message_handler(
    lambda message: (str(message.text).__eq__(russian['GET_CONTRACT_NUMBER']) or str(message.text).__eq__(
        latin['GET_CONTRACT_NUMBER']) or str(message.text).__eq__(
        translate_cyrillic_or_latin(latin['GET_CONTRACT_NUMBER'], 'cyr'))) and (not str(message.text).__eq__('/start')),
    state=ContractNumberState.begin)
async def get_contract_menu_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'SET_INN_OR_CONTRACT_NUMBER')
        await ContractNumberState.get_contract_number.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'),
                    state=ContractNumberState.get_contract_number)
async def get_contract_number_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (message.text.__eq__(latin["BACK_MENU"]) or message.text.__eq__(
                    russian["BACK_MENU"]) or message.text.__eq__(
                translate_cyrillic_or_latin(latin["BACK_MENU"], 'cyr'))):
                try:
                    inn = int(message.text)
                except Exception:
                    text = translate(data['lang'], 'SET_INN_OR_CONTRACT_NUMBER')
                    await ContractNumberState.get_contract_number.set()
                    await message.bot.send_message(text=text, chat_id=message.chat.id,
                                                   reply_markup=back_menu(data['lang']))
                update = get_contract_number(token=data['token'], inn=inn)
                if update:
                    for i in update:
                        text = f"{translate(data['lang'], 'CREATOR')}: {i['mp']}\n{translate_cyrillic_or_latin('INN', data['lang'])}:{i['inn']}\n" \
                               f"{translate(data['lang'], 'COMPANY_NAME')}:{i['company_name']}\n{translate(data['lang'], 'CONTRACT_NUMBER_CREATED_AT')}:{str(i['time'])[:10]}\n" \
                               f"{translate(data['lang'], 'CONTRACT_NUMBER')}:{i['number']}\n{translate(data['lang'], 'DISTRICT')}:{i['region']}\n{translate(data['lang'], 'MEMBER_PHONE')}:{i['phone_number']}"
                        await BaseState.base.set()
                        user = get_one_user(data['user_id'])
                        data['role'] = user['role']
                        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                                       reply_markup=base_menu(data['lang'], data['role']))
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
        text = translate(data['lang'], 'NOT_FOUND')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))
