import datetime
from os.path import join as join_path
from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import latin, russian
from api.users.users import get_one_user
from button.reply_markup import base_menu
from configs.constants import BASE_URL
from dispatch import dp
from excel_utils import check_excel
from states import BaseState


@dp.message_handler(lambda message: (str(message.text).__eq__(latin['OFFICE_MANAGER_CONTRACT_NUMBER_EXCEL'])
                                     or str(message.text).__eq__(
            russian['OFFICE_MANAGER_CONTRACT_NUMBER_EXCEL']) or str(
            message.text).__eq__(
            translate_cyrillic_or_latin(latin['OFFICE_MANAGER_CONTRACT_NUMBER_EXCEL'], 'cyr'))), state=BaseState.base)
async def contract_number_office_manager_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = "READ_OR_CREATE"
    #     year = datetime.datetime.now().year
    #     order_path = f"contract_number_{year}.xlsx"
    #     ORDER_EXCEL_PATH = join_path(BASE_URL, 'excel_utils', 'excel', 'contract_number')
    #     check_excel_params = check_excel(ORDER_EXCEL_PATH, order_path)
    #     if check_excel_params.__eq__("file yoq"):
    #         text = translate(data['lang'], "FILE_NOT_FOUND")
    #         await BaseState.base.set()
    #         user = get_one_user(data['user_id'])
    #         data['role'] = user['role']
    #         await message.bot.send_message(text=text, chat_id=message.chat.id,
    #                                        reply_markup=base_menu(data['lang'], data['role']))
    #     else:
    #         await BaseState.base.set()
    #         file = join_path(ORDER_EXCEL_PATH, order_path)
    #         user = get_one_user(data['user_id'])
    #         data['role'] = user['role']
    #         await message.bot.send_document(chat_id=message.chat.id, document=open(file, 'rb+'),
    #                                         reply_markup=base_menu(data['lang'], data['role']))
