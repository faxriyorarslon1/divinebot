from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import latin, russian
from api.users.users import get_user_phone_number, create_user, update_user
from button.inline import village_all_inline, language_choice
from button.reply_markup import to_wait_func, login, phone_number_markup
from dispatch import dp
from states import BaseState
from states.authorization.register import RegisterState


# @dp.message_handler()
@dp.message_handler(
    lambda message: str(message.text).__eq__(latin['REGISTER']) or str(message.text).__eq__(russian['REGISTER']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['REGISTER'], 'cyr')),
    state=RegisterState.begin)
async def register_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], "LANGUAGE")
        await RegisterState.language.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=language_choice(data['lang']))


@dp.callback_query_handler(state=RegisterState.language)
async def language_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['lang'] = call.data
        text = translate(data['lang'], "FIRST_NAME")
        await RegisterState.first_name.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id, reply_markup=ReplyKeyboardRemove())
        return


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=RegisterState.first_name)
async def first_name_create_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (message.text.__eq__(latin['REGISTER']) or message.text.__eq__(
                russian['REGISTER']) or message.text.__eq__(translate_cyrillic_or_latin(latin['REGISTER'], 'cyr'))):
            data['first_name'] = message.text
            text = translate(data['lang'], "VILLAGE")
            village = village_all_inline(data['lang'])
            if village:
                await RegisterState.village.set()
                await message.bot.send_message(text=text, chat_id=message.chat.id,
                                               reply_markup=village)
            return
        text = translate(data['lang'], "FIRST_NAME")
        await RegisterState.first_name.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id)


@dp.callback_query_handler(state=RegisterState.village)
async def district_create_handler(call: types.CallbackQuery, state: FSMContext):
    query = call.data
    async with state.proxy() as data:
        data['new_district'] = query[1:]
    text = translate(data['lang'], "PHONE_NUMBER_SET")
    await RegisterState.phone_number.set()
    await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                        reply_markup=phone_number_markup(data['lang']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), content_types=types.ContentType.CONTACT,
                    state=RegisterState.phone_number)
async def phone_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.contact.phone_number.startswith("+"):
            data['phone_number'] = message.contact.phone_number
        else:
            data['phone_number'] = f"+{str(message.contact.phone_number)}"
        text = translate(data['lang'], "PASSWORD_IMAGE")
        await RegisterState.password_image.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=ReplyKeyboardRemove())


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), content_types=types.ContentType.PHOTO,
                    state=RegisterState.password_image)
async def passport_image_create_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        passport_image_path = message.photo[-1].file_id
        user = get_user_phone_number(data['phone_number'])
        if user.get("message").startswith("Uzr"):
            create_user(first_name=data['first_name'],
                        district=data['new_district'],
                        phone_number=data['phone_number'],
                        passport_image_path=passport_image_path,
                        is_member=False,
                        chat_id=str(message.chat.id)
                        )
            text = translate(data['lang'], "DATA_NOT_FOUND")
            await RegisterState.to_wait.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=to_wait_func(data['lang']))
            return
        if user.get("message") == "yuq":
            update_user(first_name=data['first_name'],
                        district=data['new_district'],
                        phone_number=data['phone_number'],
                        passport_image_path=passport_image_path,
                        user_id=user.get("user_id"),
                        chat_id=message.chat.id)
            text = translate(data['lang'], "DATA_NOT_FOUND")
            await RegisterState.to_wait.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=to_wait_func(data['lang']))
            return
        if user.get("message").__eq__("bor"):
            text = translate(data['lang'], 'SUCCESSFULLY_REGISTERED')
            await RegisterState.login.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=login(data['lang']))
            return
        if user.get("message").__eq__("not member"):
            text = translate(data['lang'], "DATA_NOT_FOUND")
            await RegisterState.to_wait.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=to_wait_func(data['lang']))
            return


@dp.message_handler(
    lambda message: not str(message.text).__eq__('/start'),
    content_types=types.ContentType.ANY,
    state=RegisterState.password_image)
async def any_message_handler(message: types.Message, state: FSMContext):
    await message.delete()
    return


@dp.message_handler(
    lambda message: str(message.text).__eq__(latin["WAIT"]) or str(message.text).__eq__(russian["WAIT"]) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin["WAIT"], 'cyr')) and str(message.text).__eq__('/start'),
    state=[RegisterState.to_wait, BaseState.base])
async def to_wait_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        user = get_user_phone_number(data['phone_number'])
        if user.get("message").__eq__("bor"):
            text = translate(data['lang'], 'SUCCESSFULLY_REGISTERED')
            await RegisterState.login.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=login(data['lang']))
            return
        else:
            text = translate(data['lang'], "DATA_NOT_FOUND")
            await RegisterState.to_wait.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=to_wait_func(data['lang']))
            return
