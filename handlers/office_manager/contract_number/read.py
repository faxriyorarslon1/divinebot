from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import russian, latin
from api.orders.contract_number import ContractNumber
from api.users import district_retrieve
from api.users.users import get_one_user
from button.inline import months
from button.reply_markup import back_menu, base_menu
from dispatch import dp
from excel_utils import check_excel
from excel_utils.product_report import CONTRACT_NUMBER_EXCEL_PATH
from states import ContractNumberAllState, BaseState


@dp.message_handler(
    lambda message: (str(message.text).__eq__(russian['READ_CONTRACT_NUMBER']) or str(message.text).__eq__(
        latin['READ_CONTRACT_NUMBER']) or str(message.text).__eq__(
        translate_cyrillic_or_latin(latin['READ_CONTRACT_NUMBER'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=ContractNumberAllState.begin)
async def create_document_file(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        contract_number = ContractNumber(token=data['token']).get_excel()
        user = get_one_user(data['user_id'])
        from os.path import join as join_path
        check = check_excel(CONTRACT_NUMBER_EXCEL_PATH, contract_number['file_name'])
        if check.__eq__('bosingiz'):
            document = join_path(CONTRACT_NUMBER_EXCEL_PATH, contract_number['file_name'])
            await BaseState.base.set()
            await message.bot.send_document(chat_id=message.chat.id, document=open(document, 'rb+'),
                                            reply_markup=base_menu(lang=data['lang'], role=user['role']))
            return
        text2 = translate(data['lang'], 'FILE_NOT_FOUND')
        await BaseState.base.set()
        await message.bot.send_message(text=text2, chat_id=message.chat.id,
                                       reply_markup=base_menu(lang=data['lang'], role=user['role']))
