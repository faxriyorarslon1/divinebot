from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import latin, russian
from api.users.users import get_one_user
from button.reply_markup import base_menu, admin_document
from configs.constants import BASE_URL
from dispatch import dp
from excel_utils import check_excel
from states import BaseState, AdminDocumentState
from os.path import join as join_path


@dp.message_handler(lambda message: (str(message.text).__eq__(russian['TEST_EXCEL']) or str(message.text).__eq__(
    latin['TEST_EXCEL']) or str(message.text).__eq__(translate_cyrillic_or_latin(latin['TEST_EXCEL'], 'cyr'))) and (
                                            not str(message.text).__eq__('/start')),
                    state=BaseState.base)
async def admin_document_user_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'VIZIT_DOCUMENT_MANAGER_TEXT')
        await AdminDocumentState.base.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=admin_document(data['lang']))


@dp.message_handler(lambda message: (str(message.text).__eq__(russian['MANAGER_DOCUMENT']) or str(message.text).__eq__(
    latin['MANAGER_DOCUMENT']) or str(message.text).__eq__(
    translate_cyrillic_or_latin(latin['MANAGER_DOCUMENT'], 'cyr'))) and (not str(message.text).__eq__('/start')),
                    state=AdminDocumentState.base)
async def admin_manager_vizit_document_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        path = join_path(BASE_URL, 'excel_utils', 'excel', 'double_excel', 'doctor')
        excel_path = "pharmacy_or_vizit.xlsx"
        check_excel_params = check_excel(path, excel_path)
        if check_excel_params.__eq__("file yoq"):
            text = translate(data['lang'], "NOT_FOUND")
            await AdminDocumentState.base.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=admin_document(data['lang']))
            return
        text = translate(data['lang'], 'SUCCESSFULLY')
        await AdminDocumentState.base.set()
        excel = join_path(path, excel_path)
        await message.bot.send_document(caption=text, chat_id=message.chat.id, document=open(excel, 'rb+'),
                                        reply_markup=admin_document(data['lang']))


@dp.message_handler(lambda message: (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
    russian['BACK_MENU']) or message.text.__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                                            not str(message.text).__eq__('/start')),
                    state=[AdminDocumentState.base])
async def settings_back_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))
