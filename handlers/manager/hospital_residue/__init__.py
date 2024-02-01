from .excel_file import *
from .hospital_residue_manager import *
from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import russian, latin
from button.reply_markup import manager_hospital_residue
from dispatch import dp
from states import BaseState, ManagerHospitalVizit


@dp.message_handler(lambda message: (str(message.text).__eq__(latin['HOSPITAL_PARAMS']) or str(message.text).__eq__(
    russian['HOSPITAL_PARAMS']) or str(message.text).__eq__(
    translate_cyrillic_or_latin(latin['HOSPITAL_PARAMS'], 'cyr'))) and (not str(message.text).__eq__('/start')),
                    state=BaseState.base)
async def create_double_vizit(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'CHOICE_EXCEL_OR_HOSPITAL_VIZIT_RESIDUE')
        await ManagerHospitalVizit.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=manager_hospital_residue(data['lang']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[ManagerHospitalVizit.begin])
async def back_menu_base_menu_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))
