from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import latin, russian
from api.users.users import login_exist_user, login_user, get_one_user
from button.reply_markup import login, base_menu, phone_number_markup
from dispatch import dp
from states import BaseState
from states.authorization.login import LoginState
from states.authorization.register import RegisterState


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin["LOGIN"]) or str(message.text).__eq__(russian["LOGIN"]) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin["LOGIN"], "cyr"))) and (
                            not str(message.text).__eq__('/start')),
    state=RegisterState.login)
async def login_user_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], "PHONE_NUMBER_SET")
        await LoginState.begin.set()
        await message.bot.send_message(
            text=text,
            chat_id=message.chat.id,
            reply_markup=phone_number_markup(data['lang'])
        )


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), content_types=types.ContentType.CONTACT,
                    state=LoginState.begin)
async def check_phone_number_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if str(message.contact.phone_number).startswith("+"):
            phone = message.contact.phone_number
        else:
            phone = f"+{message.contact.phone_number}"
        user = login_exist_user(phone)
        if str(user.get("message")).startswith("Bunday"):
            text = translate(data['lang'], "BAD_PHONE_NUMBER")
            await RegisterState.login.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=login(data['lang']))
            return
        user1 = login_user(phone_number=phone)
        data['user_id'] = user1.get('user_id')
        data['token'] = user1.get("token")
        data['role'] = user1.get("role")
        user_data = get_one_user(data['user_id'])
        data['district'] = user_data['district']
        text = translate(data['lang'], "BASE_MENU")
        await BaseState.base.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))
