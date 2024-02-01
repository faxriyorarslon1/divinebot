from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate, translate_cyrillic_or_latin
from Tranlate.translate_language import latin, russian
from api.users import district_retrieve
from api.users.users import get_one_user
from button.reply_markup import base_menu
from dispatch import dp
from excel_utils import check_excel
from excel_utils.user.location import LOCATION_EXCEL_PATH
from states import BaseState
from states.bron import VizitReportState


@dp.message_handler(lambda message: (str(message.text).__eq__(russian['VIZIT_FILE']) or str(message.text).__eq__(
    latin['VIZIT_FILE']) or str(message.text).__eq__(translate_cyrillic_or_latin(latin['VIZIT_FILE'], 'cyr'))) and (
                                    not str(message.text).__eq__('/start')),
                    state=VizitReportState.location)
async def cal_back_member_list_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        from os.path import join as join_path
        year = datetime.now().year
        other_user = get_one_user(data['location_member_id'])
        user = get_one_user(data['user_id'])
        district = district_retrieve(user['district'])
        data['role'] = user['role']
        user_name = other_user['first_name']
        if other_user['last_name']:
            user_name = f"{other_user['first_name']}_{other_user['last_name']}"
        excel_path = f"{user_name}_{district['name']}_location_{year}_{data['month']}.xlsx"
        check = check_excel(LOCATION_EXCEL_PATH, excel_path)
        if check.__eq__("bosingiz"):
            document = join_path(LOCATION_EXCEL_PATH, excel_path)
            await BaseState.base.set()
            await message.bot.send_document(chat_id=message.chat.id, document=open(document, "rb+"),
                                            reply_markup=base_menu(data['lang'], data['role']))
        else:
            text = translate(data['lang'], 'NOT_FOUND')
            await BaseState.base.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=base_menu(data['lang'], data['role']))
