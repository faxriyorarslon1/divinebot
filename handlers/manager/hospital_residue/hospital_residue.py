from aiogram import types
from aiogram.dispatcher import FSMContext
from os.path import join
from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import latin, russian
from api.users.pharmacy_residue import ResidueExcel
from button.reply_markup import base_menu, manager_hospital_residue
from configs.constants import BASE_API_URL, BASE_API_NOT_VERSION
from dispatch import dp
from states import BaseState, ManagerHospitalVizit


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['EXCEL_TEXT']) or str(message.text).__eq__(
        russian['EXCEL_TEXT']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['EXCEL_TEXT'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')), state=ManagerHospitalVizit.begin)
async def manager_pharmacy_residue_handler(message: types.Message, state: FSMContext): pass
