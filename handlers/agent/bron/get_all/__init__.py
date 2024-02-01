from .confirmed import *
# from .unreviewed import *
from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import latin, russian
from button.reply_markup import bron_confirmed_or_unconfirmed_menu
from dispatch import dp
from states.bron import BronState, GetAllBronState


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['GET_ALL_ORDERS_AGENT']) or str(message.text).__eq__(
        russian['GET_ALL_ORDERS_AGENT']) or str(message.text).__eq__(
        translate_cyrillic_or_latin(latin['GET_ALL_ORDERS_AGENT'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')), state=BronState.bron)
async def agent_get_all_order_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'GET_ALL_TEXT')
        await GetAllBronState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=bron_confirmed_or_unconfirmed_menu(data['lang']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                    not str(message.text).__eq__('/start')),
    state=GetAllBronState.begin)
async def back_menu_agent_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'BACK')
        await BronState.bron.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=bron_menu(data['lang']))
