from aiogram.types import ReplyKeyboardRemove

from api.users.location import get_all_location, create_location
from excel_utils.user.location import location_excel
from states.authorization.location import LocationState
from .pharmacy import *
from .vizit import *
from aiogram import types
from aiogram.dispatcher import FSMContext
from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import latin, russian
from api.users.users import get_one_user
from button.reply_markup import hospital_or_vizit, base_menu, location_markup
from dispatch import dp
from states import BaseState
from states.double_vizit import DoubleVizitState


@dp.message_handler(lambda message: (str(message.text).__eq__(latin['DOUBLE_VIZIT']) or str(message.text).__eq__(
    russian['DOUBLE_VIZIT']) or str(message.text).__eq__(
    translate_cyrillic_or_latin(latin['DOUBLE_VIZIT'], 'cyr'))) and (not str(message.text).__eq__('/start')),
                    state=BaseState.base)
async def create_double_vizit(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text2 = translate(data['lang'], 'SEND_LOCATION')
        dat3 = get_all_location(user_id=data['user_id'], token=data['token'])
        if dat3.get('count') == 0:
            await LocationState.double_location.set()
            await message.bot.send_message(text=text2, chat_id=message.chat.id,
                                           reply_markup=back_menu(data['lang']))
            return
        text = translate(data['lang'], "HOSPITAL_OR_VIZIT")
        await DoubleVizitState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=hospital_or_vizit(data['lang']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), content_types=types.ContentType.LOCATION,
                    state=LocationState.double_location)
async def location_create_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.location.live_period:
            data['lat'], data['lan'] = message.location['latitude'], message.location["longitude"]
            created_at = datetime.now()
            user = get_one_user(data['user_id'])
            name = f"{user['first_name']}"
            if user['last_name']:
                name = f"{user['first_name']} {user['last_name']}"
            user_district = get_one_user(data['user_id'])
            data['district'] = user_district['district']
            district = district_retrieve(user_district['district'])
            location_excel(created_at, name, data['lat'], data['lan'], district.get('name'))
            create_location(lan=data['lan'], lat=data['lat'], created_by=data['user_id'], token=data['token'])
            text = translate(data['lang'], 'SUCCESS_LOCATION')
            text2 = translate(data['lang'], 'HOSPITAL_OR_VIZIT')
            await message.bot.send_message(text=text2, chat_id=message.chat.id, reply_markup=ReplyKeyboardRemove())
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=hospital_or_vizit(lang=data['lang']))
            await DoubleVizitState.begin.set()
            return
        text = translate(data['lang'], 'BAD_LOCATION')
        await LocationState.double_location.set()
        await message.bot.send_message(
            text=text, chat_id=message.chat.id
        )


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[DoubleVizitState.begin, LocationState.double_location])
async def back_menu_base_menu_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))
