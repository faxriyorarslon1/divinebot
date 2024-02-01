from .create import *
from .products_get_all import *
from .delete_product import *
from .update_product import *
from .plan_product import *
from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import latin, russian
from button.reply_markup import crud_for_office_manager
from dispatch import dp
from states import BaseState
from states.orders import OrdersState


@dp.message_handler(lambda message: (str(message.text).__eq__(latin['PRODUCTS']) or str(message.text).__eq__(
    russian['PRODUCTS']) or str(message.text).__eq__(translate_cyrillic_or_latin(latin['PRODUCTS'], 'cyr'))) and (
                                            not str(message.text).__eq__('/start')),
                    state=BaseState.base)
async def debit_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'ORDERS_MENU')
        await OrdersState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=crud_for_office_manager(data['lang']))


@dp.message_handler(lambda message: (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
    russian['BACK_MENU']) or message.text.__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                                    not str(message.text).__eq__('/start')),
                    state=OrdersState.begin)
async def create_product_the_rest_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'THE_BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))
