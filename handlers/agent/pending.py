from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import latin, russian
from api.users.users import get_one_user
from button.reply_markup import base_menu
from dispatch import dp
from states import BaseState


@dp.message_handler(lambda message: message.text.__eq__(russian['QARZDORLIK_AGENT']) or message.text.__eq__(
    latin['QARZDORLIK_AGENT']) or message.text.__eq__(translate_cyrillic_or_latin(latin['QARZDORLIK_AGENT'], 'cyr')) or
                                    message.text.__eq__(russian['INCOME_AGENT']) or message.text.__eq__(
    latin['INCOME_AGENT']) or message.text.__eq__(translate_cyrillic_or_latin(latin['INCOME_AGENT'], 'cyr')) or
                                    str(message.text).__eq__(latin['DOGOVOR']) or str(message.text).__eq__(
    russian['DOGOVOR']) or str(
    message.text).__eq__(translate_cyrillic_or_latin(latin['DOGOVOR'], 'cyr')) or str(message.text).__eq__(
    latin['BRON']) or str(message.text).__eq__(translate_cyrillic_or_latin(latin['BRON'], 'cyr')) or str(
    message.text).__eq__(russian['BRON']), state=BaseState.base)
async def pending_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'UNDER_REPAIR')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))
