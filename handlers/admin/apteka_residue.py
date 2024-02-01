import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from os.path import join
from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import latin, russian
from api.users.pharmacy_residue import ResidueExcel
from button.reply_markup import base_menu
from configs.constants import BASE_API_URL, BASE_API_NOT_VERSION
from dispatch import dp
from states import BaseState


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['ADMIN_VIZIT_RESIDUE_SEE']) or str(message.text).__eq__(
        russian['ADMIN_VIZIT_RESIDUE_SEE']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['ADMIN_VIZIT_RESIDUE_SEE'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')), state=BaseState.base)
async def admin_pharmacy_residue(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'EXCEL_FILE')
        text2 = translate(data['lang'], 'NOT_FOUND_EXCEL_FILE')
        await BaseState.base.set()
        excel = ResidueExcel(token=data['token']).get_last()
        # excel_file = f"{BASE_API_NOT_VERSION}{excel}"
        filename = excel.split('/')[-1]
        path_excel = join('excel_file', filename)
        try:
            with open(path_excel, 'rb') as file:
                await message.bot.send_message(text=text, chat_id=message.chat.id)
                await BaseState.base.set()
                await message.bot.send_document(document=file, chat_id=message.chat.id,
                                                reply_markup=base_menu(data['lang'], role=data['role']))
                os.remove(path_excel)
        except:
            import requests
            path = requests.get(url=excel)
            with open(path_excel, 'wb') as f:
                f.write(path.content)
            with open(path_excel, 'rb') as file:
                await message.bot.send_message(text=text2, chat_id=message.chat.id)
                await BaseState.base.set()
                await message.bot.send_document(document=file, chat_id=message.chat.id,
                                                reply_markup=base_menu(data['lang'], role=data['role']))
