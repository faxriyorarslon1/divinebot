import datetime
from os.path import join as join_path
from aiogram import types
from aiogram.dispatcher import FSMContext
from .create import *
from .read import *
from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import latin, russian
from api.users.users import get_one_user
from button.reply_markup import base_menu, create_or_read_contract_number
from configs.constants import BASE_URL
from dispatch import dp
from excel_utils import check_excel
from states import BaseState, ContractNumberAllState


@dp.message_handler(lambda message: (str(message.text).__eq__(latin['OFFICE_MANAGER_CONTRACT_NUMBER_EXCEL'])
                                     or str(message.text).__eq__(
            russian['OFFICE_MANAGER_CONTRACT_NUMBER_EXCEL']) or str(
            message.text).__eq__(
            translate_cyrillic_or_latin(latin['OFFICE_MANAGER_CONTRACT_NUMBER_EXCEL'], 'cyr'))), state=BaseState.base)
async def contract_number_office_manager_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], "READ_OR_CREATE")
        await ContractNumberAllState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=create_or_read_contract_number(data['lang']))
