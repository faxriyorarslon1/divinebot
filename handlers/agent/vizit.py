import os
from datetime import datetime
import pytz
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import latin, russian
from api.users import district_retrieve
from api.users.agree_doctor import agree_doctor_api
from api.users.city import create_city, city_retrieve
from api.users.doctor import create_doctor, doctor_retrieve
from api.users.hospital import Hospital
from api.users.location import get_all_location, create_location
from api.users.users import get_one_user
from button.inline import city_all_inline, doctor_all_inline, check_agreement, hospital_all_inline, \
    doctor_type_inline_button, category_doctor_inline
from button.reply_markup import base_menu, back_menu
from dispatch import dp
from excel_utils.user import create_doctor_excel
from excel_utils.user.location import location_excel
from excel_utils.vizit import create_doctor_all_excel
from states import BaseState
from states.authorization.location import LocationState
from states.vizit import VizitState, DoctorState, CityState


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin["VIZIT"]) or str(message.text).__eq__(russian["VIZIT"]) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin["VIZIT"], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=BaseState.base)
async def bron_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'VIZIT_MENU')
        text2 = translate(data['lang'], 'SEND_LOCATION')
        dat3 = get_all_location(user_id=data['user_id'], token=data['token'])
        if dat3.get('count') == 0:
            await LocationState.location.set()
            await message.bot.send_message(text=text2, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
            return
        text3 = translate(data['lang'], 'CHOICE_VIZIT')
        await VizitState.vizit.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=ReplyKeyboardRemove())
        await message.bot.send_message(text=text3, chat_id=message.chat.id,
                                       reply_markup=city_all_inline(district_id=data['district'], token=data['token'],
                                                                    created_by=data['user_id'],
                                                                    lang=data['lang']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[LocationState.location])
async def back_menu_base_menu_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), content_types=types.ContentType.LOCATION,
                    state=LocationState.location)
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
            text2 = translate(data['lang'], 'CHOICE_VIZIT')
            await message.bot.send_message(text=text2, chat_id=message.chat.id, reply_markup=ReplyKeyboardRemove())
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=city_all_inline(data['district'], data['token'],
                                                                        created_by=data['user_id'],
                                                                        lang=data['lang']))
            await VizitState.vizit.set()
            return
        text = translate(data['lang'], 'BAD_LOCATION')
        await LocationState.location.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id)


@dp.callback_query_handler(state=VizitState.vizit)
async def city_create_handler(call: types.CallbackQuery, state: FSMContext):
    props = call.data
    await call.message.delete()
    async with state.proxy() as data:
        if props == "new":
            text = translate(data['lang'], 'CITY_NAME')
            await CityState.create.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=back_menu(data['lang']))
            return
        if props == "back":
            text = translate(data['lang'], 'BACK')
            await BaseState.base.set()
            user = get_one_user(data['user_id'])
            data['role'] = user['role']
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=base_menu(data['lang'], data['role']))
            return
        data['hospital_page'] = 1
        data['city'] = props[1:]
        hospital = hospital_all_inline(page=data['hospital_page'],
                                       token=data['token'], city=data['city'], lang=data['lang'])
        if hospital:
            text = translate(data['lang'], 'LPU_CHOICE')
            await VizitState.lpu.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=hospital_all_inline(page=data['hospital_page'],
                                                                                 token=data['token'], city=data['city'],
                                                                                 lang=data['lang']))
            return
        text = translate(data['lang'], 'NOT_FOUND_LPU')
        await VizitState.create_hospital.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id)
        return


@dp.callback_query_handler(state=VizitState.lpu)
async def hospital_create_next_handler(call: types.CallbackQuery, state: FSMContext):
    props = call.data
    await call.message.delete()
    async with state.proxy() as data:
        if props.__eq__("prev"):
            data['hospital_page'] -= 1
            text = translate(data['lang'], 'LPU_CHOICE')
            await VizitState.lpu.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=hospital_all_inline(page=data['hospital_page'],
                                                                                 token=data['token'],
                                                                                 city=data['city'], lang=data['lang']))
            return
        if props.__eq__("next"):
            data['hospital_page'] += 1
            text = translate(data['lang'], 'LPU_CHOICE')
            await VizitState.lpu.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=hospital_all_inline(page=data['hospital_page'],
                                                                                 token=data['token'],
                                                                                 city=data['city'], lang=data['lang']))
            return
        if props.__eq__("back"):
            text2 = translate(data['lang'], 'CHOICE_VIZIT')
            await call.message.bot.send_message(text=text2, chat_id=call.message.chat.id,
                                                reply_markup=city_all_inline(district_id=data['district'],
                                                                             token=data['token'],
                                                                             created_by=data['user_id'],
                                                                             lang=data['lang']))
            await VizitState.vizit.set()
            return
        if props.__eq__("new"):
            text = translate(data['lang'], 'CREATE_HOSPITAL')
            await VizitState.create_hospital.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=back_menu(data['lang']))
            return
        data['hospital'] = props[1:]
        data['doctor_page'] = 1
        text = translate(data['lang'], 'CHOICE_DOCTOR')
        await VizitState.doctor.set()
        doctors = doctor_all_inline(
            hospital=data['hospital'],
            token=data['token'], lang=data['lang'], page=data['doctor_page'])
        if doctors:
            await call.message.bot.send_message(
                text=text, chat_id=call.message.chat.id,
                reply_markup=doctor_all_inline(
                    hospital=data['hospital'],
                    token=data['token'], lang=data['lang'], page=data['doctor_page'])
            )
            return
        text = translate(data['lang'], 'NEW_DOCTOR_CREATE')
        await VizitState.doctor.set()
        await call.message.bot.send_message(
            text=text, chat_id=call.message.chat.id,
            reply_markup=doctor_all_inline(
                hospital=data['hospital'],
                token=data['token'], lang=data['lang'], page=data['doctor_page'])
        )


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=CityState.create)
async def city_create_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                data['city'] = message.text
                create_city(name=data['city'], district=data['district'], created_by=data['user_id'],
                            token=data['token'])
                text2 = translate(data['lang'], 'CHOICE_CITY')
                await VizitState.vizit.set()
                await message.bot.send_message(
                    text=text2, chat_id=message.chat.id,
                    reply_markup=city_all_inline(data['district'], token=data['token'], created_by=data['user_id'],
                                                 lang=data['lang'])
                )
                return
            text = translate(data['lang'], 'BACK')
            await BaseState.base.set()
            user = get_one_user(data['user_id'])
            data['role'] = user['role']
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=base_menu(data['lang'], data['role']))
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=VizitState.create_hospital)
async def create_hospital_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                data['hospital_name'] = message.text
                Hospital(name=data['hospital_name'], city=data['city'], token=data['token']).create()
                text = translate(data['lang'], 'SUCCESS_LPU')
                await VizitState.lpu.set()
                await message.bot.send_message(
                    text=text, chat_id=message.chat.id,
                    reply_markup=hospital_all_inline(page=data['hospital_page'],
                                                     token=data['token'], city=data['city'], lang=data['lang']))
                return
            text = translate(data['lang'], 'BACK')
            await BaseState.base.set()
            user = get_one_user(data['user_id'])
            data['role'] = user['role']
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=base_menu(data['lang'], data['role']))
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.callback_query_handler(state=VizitState.doctor)
async def doctor_create_handler(call: types.CallbackQuery, state: FSMContext):
    props = call.data
    await call.message.delete()
    async with state.proxy() as data:
        if props == "back":
            text = translate(data['lang'], 'BACK')
            await VizitState.lpu.set()
            await call.message.bot.send_message(
                text=text, chat_id=call.message.chat.id,
                reply_markup=hospital_all_inline(city=data['city'], token=data['token'], page=data['hospital_page'],
                                                 lang=data['lang'])
            )
            return
        if props == "new":
            text = translate(data['lang'], 'FIO_DOCTOR')
            await DoctorState.begin.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=back_menu(data['lang']))
            return
        if props.__eq__("prev"):
            data['doctor_page'] -= 1
            text = translate(data['lang'], 'CHOICE_DOCTOR')
            await VizitState.doctor.set()
            await call.message.bot.send_message(
                text=text, chat_id=call.message.chat.id,
                reply_markup=doctor_all_inline(
                    hospital=data['hospital'],
                    token=data['token'], lang=data['lang'], page=data['doctor_page'])
            )
            return
        if props.__eq__("next"):
            data['doctor_page'] += 1
            text = translate(data['lang'], 'CHOICE_DOCTOR')
            await VizitState.doctor.set()
            await call.message.bot.send_message(
                text=text, chat_id=call.message.chat.id,
                reply_markup=doctor_all_inline(
                    hospital=data['hospital'],
                    token=data['token'], lang=data['lang'], page=data['doctor_page'])
            )
            return
        data['doctor'] = props[1:]
        text = translate(data['lang'], 'CREATE_COMMENT')
        await VizitState.comment.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id)


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=DoctorState.begin)
async def create_doctor_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                data['name'] = message.text
                text = translate(data['lang'], 'DOCTOR_PHONE')
                await DoctorState.phone_number.set()
                await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
                return
            text = translate(data['lang'], 'BACK')
            await BaseState.base.set()
            user = get_one_user(data['user_id'])
            data['role'] = user['role']
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=base_menu(data['lang'], data['role']))
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=DoctorState.phone_number)
async def doctor_phone_number_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                data['doctor_phone'] = message.text
                text = translate(data['lang'], 'DOCTOR_TYPE')
                await DoctorState.category.set()
                await message.bot.send_message(text=text, chat_id=message.chat.id,
                                               reply_markup=doctor_type_inline_button(data['lang']))
                return
            text = translate(data['lang'], 'BACK')
            await BaseState.base.set()
            user = get_one_user(data['user_id'])
            data['role'] = user['role']
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=base_menu(data['lang'], data['role']))
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.callback_query_handler(state=DoctorState.category)
async def doctor_category_handler(call: types.CallbackQuery, state: FSMContext):
    props = call.data
    await call.message.delete()
    async with state.proxy() as data:
        if props.__eq__("back"):
            text = translate(data['lang'], 'FIO_DOCTOR')
            await DoctorState.begin.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=back_menu(data['lang']))
            return
        data['category_doctor'] = props
        text = translate(data['lang'], 'DOCTOR_CATEGORY')
        await DoctorState.type.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=category_doctor_inline(data['lang']))
        return


# @dp.message_handler()

@dp.message_handler(lambda message: (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
    russian['BACK_MENU']) or message.text.__eq__(
    translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (not str(message.text).__eq__('/start')),
                    state=DoctorState.category)
async def create_product_back_menu_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'FIO_DOCTOR')
        await DoctorState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=back_menu(data['lang']))


@dp.callback_query_handler(state=DoctorState.type)
async def doctor_type_handler(call: types.CallbackQuery, state: FSMContext):
    props = call.data
    await call.message.delete()
    async with state.proxy() as data:
        if props.__eq__("back"):
            text = translate(data['lang'], 'TYPE_DOCTOR')
            await DoctorState.category.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=doctor_type_inline_button(data['lang']))
            return
        data['type_doctor'] = props
        doctor_hospital = Hospital(hospital_id=data['hospital'], token=data['token']).retrieve()
        text = f"{translate(data['lang'], 'DOCTOR_FAMILY_NAME')}\n    {data['name']}\n{translate(data['lang'], 'GET_CATEGORY')}:\n    {data['category_doctor']}\n{translate(data['lang'], 'TYPE_GET')}\n{data['type_doctor']}\n{translate(data['lang'], 'DOCTOR_PHONE_NUMBER')}\n    {data['doctor_phone']}\n{translate(data['lang'], 'HOSPITAL')}:\n    {doctor_hospital.get('name')}\n{translate(data['lang'], 'IS_AGREE_HOSPITAL')}"
        await VizitState.checked.set()
        await call.message.bot.send_message(chat_id=call.message.chat.id, reply_markup=check_agreement(data['lang']),
                                            text=text)


@dp.message_handler(lambda message: (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
    russian['BACK_MENU']) or message.text.__eq__(
    translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (not str(message.text).__eq__('/start')),
                    state=DoctorState.category)
async def create_product_back_menu_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'TYPE_DOCTOR')
        await DoctorState.category.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=doctor_type_inline_button(data['lang']))


@dp.callback_query_handler(state=VizitState.checked)
async def checked_doctor_handler(call: types.CallbackQuery, state: FSMContext):
    props = call.data
    async with state.proxy() as data:
        if props.__eq__("no"):
            text2 = translate(data['lang'], 'NO_SUCCESS')
            await VizitState.doctor.set()
            await call.message.bot.send_message(
                text=text2, chat_id=call.message.chat.id,
                reply_markup=doctor_all_inline(
                    hospital=data['hospital'],
                    token=data['token'], lang=data['lang'], page=data['doctor_page']
                )
            )
            return
        create_doctor(name=data['name'], phone_number=data['doctor_phone'],
                      category_doctor=data['category_doctor'], type_doctor=data['type_doctor'],
                      hospital=data['hospital'],
                      token=data['token'])
        text = translate(data['lang'], 'DOCTOR_SUCCESS_CREATE')
        await VizitState.doctor.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id, reply_markup=doctor_all_inline(
            hospital=data['hospital'],
            token=data['token'], lang=data['lang'], page=data['doctor_page']
        ))
        return


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=VizitState.comment)
async def doctor_comment(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                data['comment'] = message.text
                user = get_one_user(data['user_id'])
                name = f"{user['first_name']}"
                if user['last_name']:
                    name = f"{user['first_name']} {user['last_name']}"
                doctor = doctor_retrieve(doctor_id=data['doctor'], token=data['token'])
                text = f"{translate(data['lang'], 'CREATOR')}:  {translate_cyrillic_or_latin(name, data['lang'])}\n{translate(data['lang'], 'DOCTOR_NAME')}:  {doctor['name']}\n{translate(data['lang'], 'COMMENT_GET')}:  {data['comment']}\n{translate(data['lang'], 'CREATED_DATE')}:  {str(datetime.now())[:19]}"
                await VizitState.agreement.set()
                await message.bot.send_message(text=text, chat_id=message.chat.id,
                                               reply_markup=check_agreement(data['lang']))
                return
            text = translate(data['lang'], 'BACK')
            await BaseState.base.set()
            user = get_one_user(data['user_id'])
            data['role'] = user['role']
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=base_menu(data['lang'], data['role']))
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.callback_query_handler(state=VizitState.agreement)
async def check_agreement_handler(call: types.CallbackQuery, state: FSMContext):
    props = call.data
    await call.message.delete()
    async with state.proxy() as data:
        if props == "yes":
            text = translate(data['lang'], 'SUCCESSFULLY')
            doctor = doctor_retrieve(doctor_id=data["doctor"], token=data['token'])
            user_district = get_one_user(data['user_id'])
            district = district_retrieve(user_district['district'])
            lpu = Hospital(hospital_id=data['hospital'], token=data['token']).retrieve()
            city = city_retrieve(data['city'], token=data['token'])
            created_by = f"{user_district['first_name']}"
            if user_district['last_name']:
                created_by = f"{user_district['first_name']} {user_district['last_name']}"
            create_doctor_all_excel(
                created_at=str(pytz.timezone('Asia/Tashkent').localize(datetime.now()))[:19], created_by=created_by,
                doctor_name=doctor['name'], doctor_phone=doctor['phone_number'],
                village=district['name'], city=city['name'], comment=data['comment'], lpu=lpu['name'],
                phone_number=data['phone_number'], category=doctor['category_doctor'], d_type=doctor['type_doctor']
            )
            create_doctor_excel(created_at=str(pytz.timezone('Asia/Tashkent').localize(datetime.now()))[:19],
                                created_by=created_by,
                                doctor_name=doctor['name'], doctor_phone=doctor['phone_number'],
                                village=district['name'], city=city['name'], comment=data['comment'], lpu=lpu['name'],
                                phone_number=data['phone_number'])
            agree_doctor_api(doctor=data['doctor'], comment=data['comment'], check_agreement=True,
                             created_by=data['user_id'], token=data['token'])
            await BaseState.base.set()
            user = get_one_user(data['user_id'])
            data['role'] = user['role']
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=base_menu(data['lang'], data['role']))
            return
        text = translate(data['lang'], 'NO_SUCCESS')
        await VizitState.doctor.set()
        await call.message.bot.send_message(
            text=text, chat_id=call.message.chat.id,
            reply_markup=doctor_all_inline(
                hospital=data['hospital'],
                token=data['token'], lang=data['lang'], page=data['doctor_page'])
        )
        return


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['SEARCH']) or str(message.text).__eq__(latin['SEARCH']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['SEARCH'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=VizitState.doctor)
async def doctor_search_filter_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'SEARCH_DOCTOR')
        await VizitState.search.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id)


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=VizitState.search)
async def search_finish_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['search'] = message.text
        await VizitState.doctor.set()
        text = translate(data['lang'], 'CHOICE_DOCTOR')
        await message.bot.send_message(
            text=text, chat_id=message.chat.id,
            reply_markup=doctor_all_inline(
                hospital=data['hospital'],
                token=data['token'],
                lang=data['lang'],
                page=data['doctor_page']
            )
        )


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[VizitState.vizit, VizitState.doctor, VizitState.comment, VizitState.search,
           VizitState.agreement, DoctorState.type, DoctorState.begin, DoctorState.category,
           DoctorState.phone_number, VizitState.create_hospital])
async def back_menu_doctor_and_vizit_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))
