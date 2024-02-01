import requests
from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import latin, russian
from api.users.excel_for_order import OrderExcel
from api.users.users import get_one_user
from button.reply_markup import back_menu, base_menu, crud_for_office_manager
from configs.constants import BOT_TOKEN
from dispatch import dp, bot
from excel_utils.product_report import product_create_excel
from states import BaseState
from states.orders import OrdersState, CreateExcelState, GetAllProductState


@dp.message_handler(lambda message: (str(message.text).__eq__(russian['EXCEL_CREATE']) or str(message.text).__eq__(
    latin['EXCEL_CREATE']) or str(message.text).__eq__(translate_cyrillic_or_latin(latin['EXCEL_CREATE'], 'cyr'))) and (
                                            not str(message.text).__eq__('/start')),
                    state=OrdersState.begin)
async def create_product_name_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'CREATE_EXCEL_TEXT')
        await CreateExcelState.excel.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'),content_types=types.ContentType.DOCUMENT, state=CreateExcelState.excel)
async def create_excel_file_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.document.file_name.endswith('xlsx') or message.document.file_name.endswith(
                'xlsm') or message.document.file_name.endswith('xltx') or message.document.file_name.endswith('xltm'):
            data['excel'] = message.document.file_id
            data['file_name'] = message.document.file_name
            OrderExcel(token=data['token'], image=data['excel'], file_name=data['file_name']).create()
            file = await bot.get_file(data['excel'])
            file_pah = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"
            response = requests.get(file_pah)
            product_create_excel(data['file_name'], response.content)
            text = translate(lang=data['lang'], text="SUCCESSFULLY")
            await BaseState.base.set()
            user = get_one_user(data['user_id'])
            data['role'] = user['role']
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=base_menu(data['lang'], data['role']))
            return
        text = translate(data['lang'], 'BAD_EXCEL')
        await CreateExcelState.excel.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id)


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                    not str(message.text).__eq__('/start')),
    state=[CreateExcelState.excel, GetAllProductState.update, GetAllProductState.choice, GetAllProductState.get_all])
async def create_product_back_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'THE_BACK')
        await OrdersState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=crud_for_office_manager(data['lang']))
