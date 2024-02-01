from api.users.users import get_one_user
from .get_all import *
from .create import *
from .update import *
from .update_product import *
from .create_company import *
from button.reply_markup import bron_menu, base_menu
from dispatch import dp
from states import BaseState
from states.bron import BronState


@dp.message_handler(lambda message: (str(message.text).__eq__(latin['BRON']) or str(message.text).__eq__(
    translate_cyrillic_or_latin(latin['BRON'], 'cyr')) or str(message.text).__eq__(russian['BRON'])) and (
                                            not str(message.text).__eq__('/start')),
                    state=BaseState.base)
async def bron_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], "WELCOME_BRON")
        await BronState.bron.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=bron_menu(data['lang']))


@dp.message_handler(lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
    russian['BACK_MENU']) or str(message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                                            not str(message.text).__eq__('/start')),
                    state=[BronState.bron, CreateBronState.count, CreateBronState.inn, CreateBronState.comment,
                           CreateBronState.check, CreateBronState.products, CreateBronState.reply_products])
async def back_manu_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], "BASE_MENU_BACK")
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))
