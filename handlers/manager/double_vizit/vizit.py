from datetime import datetime

import pytz
from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import latin, russian
from api.check_mp import check_mp_create_vizit
from api.users import district_retrieve
from api.users.city import create_city, city_retrieve
from api.users.doctor import create_doctor, doctor_retrieve
from api.users.hospital import Hospital
from api.users.users import get_one_user
from button.inline import check_basket, get_all_agent, city_all_inline, hospital_all_inline, doctor_all_inline, \
    doctor_type_inline_button, category_doctor_inline, check_agreement, choice_type
from button.reply_markup import back_menu, hospital_or_vizit, base_menu
from dispatch import dp
from excel_utils.vizit import create_mp_doctor_or_pharmacy_all_excel
from states import BaseState
from states.double_vizit import DoubleVizitState
from states.vizit import CityState, VizitState


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['MANAGER_VIZIT']) or str(message.text).__eq__(
        russian['MANAGER_VIZIT']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['MANAGER_VIZIT'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')), state=DoubleVizitState.begin)
async def double_vizit_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'MANAGER_FOR_CREATE')
        text2 = translate(data['lang'], 'OR_THE_BACK')
        await DoubleVizitState.vizit.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
        await message.bot.send_message(text=text2, chat_id=message.chat.id, reply_markup=check_basket(data['lang']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[DoubleVizitState.vizit, DoubleVizitState.search_or_submit])
async def back_menu_begin_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'BACK')
        await DoubleVizitState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=hospital_or_vizit(data['lang']))


@dp.callback_query_handler(state=DoubleVizitState.vizit)
async def choice_mp_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['mp_manager'] = False
        district = get_one_user(data['user_id'])
        data['user_district'] = district['district']
        if call.data.__eq__('yes'):
            data['mp_manager'] = True
            data['page'] = 1
            data['search'] = None
            get_all = get_all_agent(lang=data['lang'], page=data['page'], first_name=None,
                                    district=district['district'], token=data['token'])
            if get_all:
                text = translate(data['lang'], 'CHOICE_MANAGER')
                await DoubleVizitState.search_or_submit.set()
                await call.message.bot.send_message(text=text, chat_id=call.message.chat.id, reply_markup=get_all)
                return
            text = translate(data['lang'], 'NOT_FOUND')
            await DoubleVizitState.begin.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=hospital_or_vizit(data['lang']))
            return
        text = translate(data['lang'], 'CHOICE_VIZIT')
        await DoubleVizitState.city.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=city_all_inline(data['user_district'], data['token'],
                                                                         lang=data['lang'], created_by=data['user_id']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=DoubleVizitState.search_or_submit)
async def search_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        get_all = get_all_agent(lang=data['lang'], page=data['page'], first_name=message.text,
                                district=data['district'],
                                token=data['token'])
        data['search'] = message.text
        if get_all:
            text = translate(data['lang'], 'CHOICE_MANAGER')
            await DoubleVizitState.search_or_submit.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=get_all)
            return
        text = translate(data['lang'], 'NOT_FOUND')
        await DoubleVizitState.search_or_submit.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=get_all_agent(lang=data['lang'], page=data['page'],
                                                                  first_name=None,
                                                                  district=data['user_district'],
                                                                  token=data['token']))


@dp.callback_query_handler(state=DoubleVizitState.search_or_submit)
async def call_mp_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data.__eq__('prev'):
            text = translate(data['lang'], 'PREV')
            data['page'] -= 1
            await DoubleVizitState.search_or_submit.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=get_all_agent(lang=data['lang'], page=data['page'],
                                                                           first_name=data['search'],
                                                                           district=data['user_district'],
                                                                           token=data['token']))
            return
        if call.data.__eq__('next'):
            text = translate(data['lang'], 'NEXT')
            data['page'] += 1
            await DoubleVizitState.search_or_submit.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=get_all_agent(lang=data['lang'], page=data['page'],
                                                                           first_name=data['search'],
                                                                           district=data['user_district'],
                                                                           token=data['token']))
            return
        if data['mp_manager']:
            data['mp'] = call.data[1:]
            text = translate(data['lang'], 'CHOICE_VIZIT')
            await DoubleVizitState.city.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=city_all_inline(data['user_district'], data['token'],
                                                                             lang=data['lang'], created_by=data['mp']))
        else:
            data['mp'] = call.data[1:]
            text = translate(data['lang'], 'CHOICE_VIZIT')
            await DoubleVizitState.city.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=city_all_inline(data['user_district'], data['token'],
                                                                             lang=data['lang'],
                                                                             created_by=data['user_id']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[DoubleVizitState.city])
async def back_menu_begin_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if data['mp_manager']:
            text = translate(data['lang'], 'BACK')
            await DoubleVizitState.search_or_submit.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=get_all_agent(lang=data['lang'], page=data['page'],
                                                                      first_name=data['search'],
                                                                      district=data['user_district'],
                                                                      token=data['token']))
            return
        text = translate(data['lang'], 'BACK')
        await DoubleVizitState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=hospital_or_vizit(data['lang']))


@dp.callback_query_handler(state=DoubleVizitState.city)
async def call_city_handler(call: types.CallbackQuery, state: FSMContext):
    props = call.data
    await call.message.delete()
    async with state.proxy() as data:
        if props == "new":
            text = translate(data['lang'], 'CITY_NAME')
            await DoubleVizitState.create_city.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=back_menu(data['lang']))
            return
        if props == "back":
            if data['mp_manager']:
                text = translate(data['lang'], 'BACK')
                await DoubleVizitState.search_or_submit.set()
                await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                    reply_markup=get_all_agent(lang=data['lang'], page=data['page'],
                                                                               first_name=data['search'],
                                                                               district=data['user_district'],
                                                                               token=data['token']))
                return
            text = translate(data['lang'], 'BACK')
            await DoubleVizitState.begin.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=hospital_or_vizit(data['lang']))
            return
        data['hospital_page'] = 1
        data['city'] = props[1:]
        hospital = hospital_all_inline(page=data['hospital_page'],
                                       token=data['token'], city=data['city'],
                                       lang=data['lang'])
        if hospital:
            text = translate(data['lang'], 'LPU_CHOICE')
            await DoubleVizitState.lpu.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=hospital)
            return
        text = translate(data['lang'], 'NOT_FOUND_LPU')
        await DoubleVizitState.create_hospital.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id)
        return


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[DoubleVizitState.lpu])
async def back_menu_begin_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if data['mp_manager']:
            text2 = translate(data['lang'], 'CHOICE_VIZIT')
            await message.bot.send_message(text=text2, chat_id=message.chat.id,
                                           reply_markup=city_all_inline(data['user_district'], data['token'],
                                                                        lang=data['lang'],
                                                                        created_by=data['mp']))
        else:
            text2 = translate(data['lang'], 'CHOICE_VIZIT')
            await message.bot.send_message(text=text2, chat_id=message.chat.id,
                                           reply_markup=city_all_inline(data['user_district'], data['token'],
                                                                        lang=data['lang'],
                                                                        created_by=data['user_id']))

        await DoubleVizitState.city.set()


@dp.callback_query_handler(state=DoubleVizitState.lpu)
async def hospital_create_next_handler(call: types.CallbackQuery, state: FSMContext):
    props = call.data
    await call.message.delete()
    async with state.proxy() as data:
        if props.__eq__("prev"):
            data['hospital_page'] -= 1
            text = translate(data['lang'], 'LPU_CHOICE')
            await DoubleVizitState.lpu.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=hospital_all_inline(page=data['hospital_page'],
                                                                                 token=data['token'],
                                                                                 city=data['city'],
                                                                                 lang=data['lang']))
            return
        if props.__eq__("next"):
            data['hospital_page'] += 1
            text = translate(data['lang'], 'LPU_CHOICE')
            await DoubleVizitState.lpu.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=hospital_all_inline(page=data['hospital_page'],
                                                                                 token=data['token'],
                                                                                 city=data['city'],
                                                                                 lang=data['lang'])
                                                )
            return
        if props.__eq__("back"):
            if data['mp_manager']:
                text2 = translate(data['lang'], 'CHOICE_VIZIT')
                await call.message.bot.send_message(text=text2, chat_id=call.message.chat.id,
                                                    reply_markup=city_all_inline(data['user_district'], data['token'],
                                                                                 lang=data['lang'],
                                                                                 created_by=data['mp']))
            else:
                text2 = translate(data['lang'], 'CHOICE_VIZIT')
                await call.message.bot.send_message(text=text2, chat_id=call.message.chat.id,
                                                    reply_markup=city_all_inline(data['user_district'], data['token'],
                                                                                 lang=data['lang'],
                                                                                 created_by=data['user_id']))

            await DoubleVizitState.city.set()
            return
        if props.__eq__("new"):
            text = translate(data['lang'], 'CREATE_HOSPITAL')
            await DoubleVizitState.create_hospital.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=back_menu(data['lang']))
            return
        data['hospital'] = props[1:]
        data['doctor_page'] = 1
        text = translate(data['lang'], 'CHOICE_DOCTOR')
        await DoubleVizitState.doctor.set()
        doctors = doctor_all_inline(
            hospital=data['hospital'],
            token=data['token'], page=data['doctor_page'])
        if doctors:
            await call.message.bot.send_message(
                text=text, chat_id=call.message.chat.id,
                reply_markup=doctor_all_inline(
                    hospital=data['hospital'],
                    token=data['token'],
                    lang=data['lang'], page=data['doctor_page']
                )
            )
            return
        text = translate(data['lang'], 'NEW_DOCTOR_CREATE')
        await DoubleVizitState.doctor.set()
        await call.message.bot.send_message(
            text=text, chat_id=call.message.chat.id,
            reply_markup=doctor_all_inline(
                hospital=data['hospital'],
                token=data['token'],
                lang=data['lang'],
                page=data['doctor_page']
            )
        )


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=DoubleVizitState.create_city)
async def city_create_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                data['city'] = message.text
                if data['mp_manager']:
                    create_city(name=data['city'], district=data['district'], token=data['token'],
                                created_by=data['mp'])
                    text2 = translate(data['lang'], 'CHOICE_CITY')
                    await DoubleVizitState.city.set()
                    await message.bot.send_message(
                        text=text2, chat_id=message.chat.id,
                        reply_markup=city_all_inline(data['district'], token=data['token'], lang=data['lang'],
                                                     created_by=data['mp'])
                    )
                else:
                    create_city(name=data['city'], district=data['district'], token=data['token'],
                                created_by=data['user_id'])
                    text2 = translate(data['lang'], 'CHOICE_CITY')
                    await DoubleVizitState.city.set()
                    await message.bot.send_message(
                        text=text2, chat_id=message.chat.id,
                        reply_markup=city_all_inline(data['district'], token=data['token'], lang=data['lang'],
                                                     created_by=data['user_id']))
                return
            text = translate(data['lang'], 'BACK')
            await DoubleVizitState.city.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=city_all_inline(district_id=data['user_district'],
                                                                        token=data['token'], lang=data['lang'],
                                                                        created_by=data['user_id']))
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=DoubleVizitState.create_hospital)
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
                await DoubleVizitState.lpu.set()
                await message.bot.send_message(
                    text=text, chat_id=message.chat.id,
                    reply_markup=hospital_all_inline(
                        page=data['hospital_page'],
                        token=data['token'],
                        city=data['city'],
                        lang=data['lang']))
                return
            text = translate(data['lang'], 'BACK')
            await DoubleVizitState.lpu.set()
            await message.bot.send_message(
                text=text, chat_id=message.chat.id,
                reply_markup=hospital_all_inline(page=data['hospital_page'],
                                                 token=data['token'],
                                                 city=data['city'],
                                                 lang=data['lang']))
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[DoubleVizitState.doctor])
async def back_menu_begin_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'BACK')
        await DoubleVizitState.lpu.set()
        await message.bot.send_message(
            text=text, chat_id=message.chat.id,
            reply_markup=hospital_all_inline(city=data['city'],
                                             token=data['token'],
                                             page=data['hospital_page'],
                                             lang=data['lang'])
        )
        return


@dp.callback_query_handler(state=DoubleVizitState.doctor)
async def doctor_create_handler(call: types.CallbackQuery, state: FSMContext):
    props = call.data
    await call.message.delete()
    async with state.proxy() as data:
        if props == "back":
            text = translate(data['lang'], 'BACK')
            await DoubleVizitState.lpu.set()
            await call.message.bot.send_message(
                text=text, chat_id=call.message.chat.id,
                reply_markup=hospital_all_inline(city=data['city'],
                                                 token=data['token'],
                                                 page=data['hospital_page'],
                                                 lang=data['lang'])
            )
            return
        if props == "new":
            text = translate(data['lang'], 'FIO_DOCTOR')
            await DoubleVizitState.create_doctor.set()
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
        await DoubleVizitState.comment.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id)


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=DoubleVizitState.create_doctor)
async def create_doctor_full_name_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                data['name'] = message.text
                text = translate(data['lang'], 'DOCTOR_PHONE')
                await DoubleVizitState.phone_number.set()
                await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
                return
            text = translate(data['lang'], 'BACK')
            await DoubleVizitState.doctor.set()
            await message.bot.send_message(
                text=text, chat_id=message.chat.id,
                reply_markup=doctor_all_inline(
                    hospital=data['hospital'],
                    token=data['token'], page=data['doctor_page'])
            )
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=DoubleVizitState.phone_number)
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
                await DoubleVizitState.category.set()
                await message.bot.send_message(text=text, chat_id=message.chat.id,
                                               reply_markup=doctor_type_inline_button(data['lang']))
                return
            text = translate(data['lang'], 'DOCTOR_PHONE')
            await DoubleVizitState.phone_number.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[DoubleVizitState.category])
async def back_menu_begin_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'FIO_DOCTOR')
        await DoubleVizitState.create_doctor.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=back_menu(data['lang']))
        return


@dp.callback_query_handler(state=DoubleVizitState.category)
async def double_doctor_category_handler(call: types.CallbackQuery, state: FSMContext):
    props = call.data
    await call.message.delete()
    async with state.proxy() as data:
        if props.__eq__("back"):
            text = translate(data['lang'], 'FIO_DOCTOR')
            await DoubleVizitState.create_doctor.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=back_menu(data['lang']))
            return
        data['category_doctor'] = props
        text = translate(data['lang'], 'DOCTOR_CATEGORY')
        await DoubleVizitState.type.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=category_doctor_inline(data['lang']))
        return


@dp.message_handler(lambda message: (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
    russian['BACK_MENU']) or message.text.__eq__(
    translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (not str(message.text).__eq__('/start')),
                    state=DoubleVizitState.type)
async def create_product_back_menu_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        # if props.__eq__("back"):
        text = translate(data['lang'], 'TYPE_DOCTOR')
        await DoubleVizitState.category.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=doctor_type_inline_button(data['lang']))
        return


@dp.callback_query_handler(state=DoubleVizitState.type)
async def doctor_type_handler(call: types.CallbackQuery, state: FSMContext):
    props = call.data
    await call.message.delete()
    async with state.proxy() as data:
        if props.__eq__("back"):
            text = translate(data['lang'], 'TYPE_DOCTOR')
            await DoubleVizitState.category.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=doctor_type_inline_button(data['lang']))
            return
        data['type_doctor'] = props
        doctor_hospital = Hospital(hospital_id=data['hospital'], token=data['token']).retrieve()
        text = f"{translate(data['lang'], 'DOCTOR_FAMILY_NAME')}\n    {data['name']}\n{translate(data['lang'], 'GET_CATEGORY')}:\n    {data['category_doctor']}\n{translate(data['lang'], 'TYPE_GET')}\n{data['type_doctor']}\n{translate(data['lang'], 'DOCTOR_PHONE_NUMBER')}\n    {data['doctor_phone']}\n{translate(data['lang'], 'HOSPITAL')}:\n    {doctor_hospital.get('name')}\n{translate(data['lang'], 'IS_AGREE_HOSPITAL')}"
        await DoubleVizitState.checked.set()
        await call.message.bot.send_message(chat_id=call.message.chat.id, reply_markup=check_agreement(data['lang']),
                                            text=text)


@dp.message_handler(lambda message: (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
    russian['BACK_MENU']) or message.text.__eq__(
    translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (not str(message.text).__eq__('/start')),
                    state=DoubleVizitState.checked)
async def create_product_back_menu_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'TYPE_DOCTOR')
        await DoubleVizitState.category.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=doctor_type_inline_button(data['lang']))


@dp.callback_query_handler(state=DoubleVizitState.checked)
async def checked_doctor_handler(call: types.CallbackQuery, state: FSMContext):
    props = call.data
    await call.message.delete()
    async with state.proxy() as data:
        if props.__eq__("no"):
            text2 = translate(data['lang'], 'NO_SUCCESS')
            await DoubleVizitState.doctor.set()
            await call.message.bot.send_message(
                text=text2, chat_id=call.message.chat.id,
                reply_markup=doctor_all_inline(
                    hospital=data['hospital'],
                    token=data['token'],
                    lang=data['lang'], page=data['doctor_page']
                )
            )
            return
        create_doctor(name=data['name'], phone_number=data['doctor_phone'],
                      category_doctor=data['category_doctor'], type_doctor=data['type_doctor'],
                      hospital=data['hospital'],
                      token=data['token'])
        text = translate(data['lang'], 'DOCTOR_SUCCESS_CREATE')
        await DoubleVizitState.doctor.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id, reply_markup=doctor_all_inline(
            hospital=data['hospital'],
            token=data['token'],
            lang=data['lang'], page=data['doctor_page']
        ))
        return


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=DoubleVizitState.comment)
async def doctor_comment(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                data['comment'] = message.text
                doctor = doctor_retrieve(doctor_id=data['doctor'], token=data['token'])
                user = get_one_user(data['user_id'])
                name = user['first_name']
                if user['last_name']:
                    name = f"{user['first_name']} {user['last_name']}"
                if data['mp_manager']:
                    text = f"{translate(data['lang'], 'CREATOR')}:  {name}\n{translate(data['lang'], 'DOCTOR_NAME')}:  {doctor['name']}\n{translate(data['lang'], 'COMMENT_GET')}:  {data['comment']}\n{translate(data['lang'], 'CREATED_DATE')}:  {str(datetime.now())[:19]}"
                    await DoubleVizitState.agreement.set()
                    await message.bot.send_message(text=text, chat_id=message.chat.id,
                                                   reply_markup=check_agreement(data['lang']))
                    return
                text = f"{translate(data['lang'], 'CREATOR')}:  {name}\n{translate(data['lang'], 'DOCTOR_NAME')}:  {doctor['name']}\n{translate(data['lang'], 'COMMENT_GET')}:  {data['comment']}\n{translate(data['lang'], 'CREATED_DATE')}:  {str(datetime.now())[:19]}"
                await DoubleVizitState.finish_vizit.set()
                await message.bot.send_message(text=text, chat_id=message.chat.id,
                                               reply_markup=check_agreement(data['lang']))
                return
            text = translate(data['lang'], 'BACK')
            await DoubleVizitState.doctor.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=doctor_all_inline(
                hospital=data['hospital'],
                token=data['token'],
                lang=data['lang'], page=data['doctor_page']
            ))
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.callback_query_handler(state=DoubleVizitState.agreement)
async def check_agreement_handler(call: types.CallbackQuery, state: FSMContext):
    props = call.data
    await call.message.delete()
    async with state.proxy() as data:
        if props == "yes":
            text = f"{translate(data['lang'], 'EVALUATION')}\n\n{translate(data['lang'], 'PREPARATION')}"
            await DoubleVizitState.preparation.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id, reply_markup=choice_type())
        else:
            text = translate(data['lang'], 'BACK')
            await DoubleVizitState.doctor.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id, reply_markup=doctor_all_inline(
                hospital=data['hospital'],
                token=data['token'],
                lang=data['lang'], page=data['doctor_page']
            ))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[DoubleVizitState.agreement, DoubleVizitState.preparation])
async def back_menu_begin_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'BACK')
        await DoubleVizitState.doctor.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=doctor_all_inline(
            hospital=data['hospital'],
            token=data['token'],
            lang=data['lang'], page=data['doctor_page']
        ))


@dp.callback_query_handler(state=DoubleVizitState.preparation)
async def preparation_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['preparation'] = call.data[1:]
        text = translate(data['lang'], 'COMMUNICATION')
        await DoubleVizitState.communication.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id, reply_markup=choice_type())


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[DoubleVizitState.communication])
async def back_menu_begin_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = f"{translate(data['lang'], 'EVALUATION')}\n\n{translate(data['lang'], 'PREPARATION')}"
        await DoubleVizitState.preparation.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=choice_type())


@dp.callback_query_handler(state=DoubleVizitState.communication)
async def communication_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['communication'] = call.data[1:]
        text = translate(data['lang'], 'THE_NEED')
        await DoubleVizitState.the_need.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id, reply_markup=choice_type())


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[DoubleVizitState.the_need])
async def back_menu_begin_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = f"{translate(data['lang'], 'COMMUNICATION')}"
        await DoubleVizitState.communication.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=choice_type())


@dp.callback_query_handler(state=DoubleVizitState.the_need)
async def the_need_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['the_need'] = call.data[1:]
        text = translate(data['lang'], 'PRESENTATION')
        await DoubleVizitState.presentation.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id, reply_markup=choice_type())


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[DoubleVizitState.presentation])
async def back_menu_begin_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'THE_NEED')
        await DoubleVizitState.the_need.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=choice_type())


@dp.callback_query_handler(state=DoubleVizitState.presentation)
async def the_need_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['presentation'] = call.data[1:]
        text = translate(data['lang'], 'PROTEST')
        await DoubleVizitState.protest.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id, reply_markup=choice_type())


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[DoubleVizitState.protest])
async def back_menu_begin_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'PRESENTATION')
        await DoubleVizitState.presentation.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=choice_type())


@dp.callback_query_handler(state=DoubleVizitState.protest)
async def the_need_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['protest'] = call.data[1:]
        text = translate(data['lang'], 'AGREEMENT')
        await DoubleVizitState.agreement_.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id, reply_markup=choice_type())


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[DoubleVizitState.agreement_])
async def back_menu_begin_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'PROTEST')
        await DoubleVizitState.protest.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=choice_type())


@dp.callback_query_handler(state=DoubleVizitState.agreement_)
async def the_need_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['agreement'] = call.data[1:]
        text = translate(data['lang'], 'ANALYSIS')
        await DoubleVizitState.analysis.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id, reply_markup=choice_type())


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[DoubleVizitState.agreement_])
async def back_menu_begin_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'AGREEMENT')
        await DoubleVizitState.agreement_.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=choice_type())


@dp.callback_query_handler(state=DoubleVizitState.analysis)
async def the_need_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['analysis'] = call.data[1:]
        if data['mp_manager']:
            mp = get_one_user(data['mp'])
            mp = f"{mp.get('first_name')} {mp.get('last_name')}"
        else:
            mp = "Ma'lumot yo'q"
        text = translate(data['lang'], 'SUCCESSFULLY')
        doctor = doctor_retrieve(doctor_id=data["doctor"], token=data['token'])
        district = district_retrieve(data['user_district'])
        lpu = Hospital(hospital_id=data['hospital'], token=data['token']).retrieve()
        city = city_retrieve(data['city'], token=data['token'])
        user = get_one_user(data['user_id'])
        created_by = user['first_name']
        if user['last_name']:
            created_by = f"{user['first_name']} {user['last_name']}"
        create_mp_doctor_or_pharmacy_all_excel(
            created_at=str(pytz.timezone('Asia/Tashkent').localize(datetime.now()))[:19], created_by=created_by,
            doctor_name=doctor['name'],
            village=district['name'], city=city['name'], comment=data['comment'], lpu=lpu['name'],
            category=doctor['category_doctor'], d_type=doctor['type_doctor'], mp=mp,
            presentation=data['presentation'], preparation=data['preparation'],
            analysis=data['analysis'], the_need=data['the_need'],
            agreement=data['agreement'], communication=data['communication'],
            doctor_phone=doctor['phone_number'],
            protest=data['protest'], pharmacy_address="No'malum", pharmacy_name="No'malum"
        )
        check_mp_create_vizit(mp=mp, city=data['city'], lpu=data['hospital'], comment=data['comment'],
                              preparation=data['preparation'], communication=data['communication'],
                              the_need=data['the_need'], presentation=data['presentation'], protest=data['protest'],
                              agreement=data['agreement'], analysis=data['analysis'], token=data['token'],
                              doctor=data['doctor'])
        await DoubleVizitState.begin.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=hospital_or_vizit(data['lang']))


@dp.callback_query_handler(state=DoubleVizitState.finish_vizit)
async def agent_final_state_for_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'SUCCESSFULLY')
        doctor = doctor_retrieve(doctor_id=data["doctor"], token=data['token'])
        district = district_retrieve(data['user_district'])
        lpu = Hospital(hospital_id=data['hospital'], token=data['token']).retrieve()
        city = city_retrieve(data['city'], token=data['token'])
        user = get_one_user(data['user_id'])
        created_by = user['first_name']
        if user['last_name']:
            created_by = f"{user['first_name']} {user['last_name']}"
        create_mp_doctor_or_pharmacy_all_excel(
            created_at=str(pytz.timezone('Asia/Tashkent').localize(datetime.now()))[:19], created_by=created_by,
            doctor_name=doctor['name'],
            village=district['name'], city=city['name'], comment=data['comment'], lpu=lpu['name'],
            category=doctor['category_doctor'], d_type=doctor['type_doctor'], mp="Ma'lumot yo'q",
            presentation="Ma'lumot yo'q", preparation="Ma'lumot yo'q",
            analysis="Ma'lumot yo'q", the_need="Ma'lumot yo'q",
            agreement="Ma'lumot yo'q", communication="Ma'lumot yo'q", protest="Ma'lumot yo'q",
            doctor_phone=doctor['phone_number'],
            pharmacy_address="No'malum", pharmacy_name="No'malum"
        )
        check_mp_create_vizit(mp="Ma'lumot yo'q", city=data['city'], lpu=data['hospital'], comment=data['comment'],
                              presentation="Ma'lumot yo'q", preparation="Ma'lumot yo'q",
                              analysis="Ma'lumot yo'q", the_need="Ma'lumot yo'q",
                              agreement="Ma'lumot yo'q", communication="Ma'lumot yo'q", protest="Ma'lumot yo'q",
                              token=data['token'],
                              doctor=data['doctor'])
        await DoubleVizitState.begin.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=hospital_or_vizit(data['lang']))
    #     text = translate(data['lang'], 'SUCCESSFULLY')
    #     district = district_retrieve(data['user_district'])
    #     pharmacy = Pharmacy(pharmacy_id=data['pharmacy'], token=data['token']).retrieve()
    #     city = city_retrieve(data['city'], token=data['token'])
    #     user = get_one_user(data['user_id'])
    #     created_by = user['first_name']
    #     if user['last_name']:
    #         created_by = f"{user['first_name']} {user['last_name']}"
    #     create_mp_doctor_or_pharmacy_all_excel(
    #         created_at=str(pytz.timezone('Asia/Tashkent').localize(datetime.now()))[:19], created_by=created_by,
    #         village=district['name'], city=city['name'], comment=data['comment'], mp="Ma'lumot yo'q",
    #         presentation="Ma'lumot yo'q", preparation="Ma'lumot yo'q",
    #         analysis="Ma'lumot yo'q", the_need="Ma'lumot yo'q",
    #         agreement="Ma'lumot yo'q", communication="Ma'lumot yo'q",
    #         protest="Ma'lumot yo'q", pharmacy_name=pharmacy['name'], pharmacy_address=pharmacy['address'],
    #         doctor_name="No'malum", doctor_phone="No'malum", lpu="No'malum", d_type="No'malum", category="No'malum"
    #     )
    #     check_mp_create_pharmacy(mp="Ma'lumot yo'q", city=data['city'], pharmacy=data['pharmacy'],
    #                              comment=data['comment'],
    #                              presentation="Ma'lumot yo'q", preparation="Ma'lumot yo'q",
    #                              analysis="Ma'lumot yo'q", the_need="Ma'lumot yo'q",
    #                              agreement="Ma'lumot yo'q", communication="Ma'lumot yo'q", protest="Ma'lumot yo'q",
    #                              token=data['token'])
    # await DoubleVizitState.begin.set()
    # await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
    #                                     reply_markup=hospital_or_vizit(data['lang']))
