from datetime import datetime

import pytz
from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import latin, russian
from api.check_mp import check_mp_create_pharmacy
from api.users import district_retrieve
from api.users.city import create_city, city_retrieve
from api.users.pharmacy import Pharmacy
from api.users.users import get_one_user
from button.inline import check_basket, get_all_agent, city_all_inline, hospital_all_inline, pharmacy_all_inline, \
    check_agreement, choice_type
from button.reply_markup import back_menu, hospital_or_vizit, base_menu
from dispatch import dp
from excel_utils.vizit import create_mp_doctor_or_pharmacy_all_excel
from states import BaseState
from states.double_vizit import DoubleVizitState


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['PHARMACY']) or str(message.text).__eq__(
        russian['PHARMACY']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['PHARMACY'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')), state=DoubleVizitState.begin)
async def double_vizit_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'MANAGER_FOR_CREATE')
        text2 = translate(data['lang'], 'OR_THE_BACK')
        await DoubleVizitState.pharmacy_vizit.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
        await message.bot.send_message(text=text2, chat_id=message.chat.id, reply_markup=check_basket(data['lang']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[DoubleVizitState.pharmacy_vizit, DoubleVizitState.search_or_submit_pharmacy])
async def back_menu_begin_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'BACK')
        await DoubleVizitState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=hospital_or_vizit(data['lang']))


@dp.callback_query_handler(state=DoubleVizitState.pharmacy_vizit)
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
                                    district=district['district'],
                                    token=data['token'])
            if get_all:
                text = translate(data['lang'], 'CHOICE_MANAGER')
                await DoubleVizitState.search_or_submit_pharmacy.set()
                await call.message.bot.send_message(text=text, chat_id=call.message.chat.id, reply_markup=get_all)
                return
            text = translate(data['lang'], 'NOT_FOUND')
            await DoubleVizitState.begin.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=hospital_or_vizit(data['lang']))
            return
        text = translate(data['lang'], 'CHOICE_VIZIT')
        await DoubleVizitState.pharmacy_city.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=city_all_inline(data['user_district'], data['token'],
                                                                         lang=data['lang'], created_by=data['user_id']))


@dp.callback_query_handler(state=DoubleVizitState.search_or_submit_pharmacy)
async def call_mp_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data.__eq__('prev'):
            text = translate(data['lang'], 'PREV')
            data['page'] -= 1
            await DoubleVizitState.search_or_submit_pharmacy.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=get_all_agent(lang=data['lang'], page=data['page'],
                                                                           first_name=data['search'],
                                                                           district=data['user_district'],
                                                                           token=data['token']))
            return
        if call.data.__eq__('next'):
            text = translate(data['lang'], 'NEXT')
            data['page'] += 1
            await DoubleVizitState.search_or_submit_pharmacy.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=get_all_agent(lang=data['lang'], page=data['page'],
                                                                           first_name=data['search'],
                                                                           district=data['user_district'],
                                                                           token=data['token']))
            return
        if data['mp_manager']:
            data['mp'] = call.data[1:]
            text = translate(data['lang'], 'CHOICE_VIZIT')
            await DoubleVizitState.pharmacy_city.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=city_all_inline(data['user_district'], data['token'],
                                                                             lang=data['lang'], created_by=data['mp']))
        else:
            data['mp'] = call.data[1:]
            text = translate(data['lang'], 'CHOICE_VIZIT')
            await DoubleVizitState.pharmacy_city.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=city_all_inline(data['user_district'], data['token'],
                                                                             lang=data['lang'],
                                                                             created_by=data['user_id']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[DoubleVizitState.pharmacy_city])
async def back_menu_begin_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if data['mp_manager']:
            text = translate(data['lang'], 'BACK')
            await DoubleVizitState.search_or_submit_pharmacy.set()
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


@dp.callback_query_handler(state=DoubleVizitState.pharmacy_city)
async def call_city_handler(call: types.CallbackQuery, state: FSMContext):
    props = call.data
    await call.message.delete()
    async with state.proxy() as data:
        if props == "new":
            text = translate(data['lang'], 'CITY_NAME')
            await DoubleVizitState.create_pharmacy_city.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=back_menu(data['lang']))
            return
        if props == "back":
            if data['mp_manager']:
                text = translate(data['lang'], 'BACK')
                await DoubleVizitState.search_or_submit_pharmacy.set()
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
        data['pharmacy_page'] = 1
        data['city'] = props[1:]
        # hospital = pharmacy_all_inline(page=data['pharmacy_page'],
        #                                token=data['token'], city=data['city'], lang=data['lang'])
        text = translate(data['lang'], 'PHARMACY_CHOICE')
        await DoubleVizitState.pharmacy.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=pharmacy_all_inline(page=data['pharmacy_page'],
                                                                             token=data['token'], city=data['city'],
                                                                             lang=data['lang']))
        return


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[DoubleVizitState.pharmacy])
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
        await DoubleVizitState.pharmacy_city.set()
        return


@dp.callback_query_handler(state=DoubleVizitState.pharmacy)
async def hospital_create_next_handler(call: types.CallbackQuery, state: FSMContext):
    props = call.data
    # await call.message.delete()
    async with state.proxy() as data:
        if props.__eq__("prev"):
            data['pharmacy_page'] -= 1
            text = translate(data['lang'], 'PHARMACY_CHOICE')
            await DoubleVizitState.pharmacy.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=pharmacy_all_inline(page=data['pharmacy_page'],
                                                                                 token=data['token'],
                                                                                 city=data['city'], lang=data['lang']))
            return
        if props.__eq__("next"):
            data['pharmacy_page'] += 1
            text = translate(data['lang'], 'PHARMACY_CHOICE')
            await DoubleVizitState.pharmacy.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=pharmacy_all_inline(page=data['pharmacy_page'],
                                                                                 token=data['token'],
                                                                                 city=data['city'], lang=data['lang']))
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
            await DoubleVizitState.pharmacy_city.set()
            return
        if props.__eq__("new"):
            text = translate(data['lang'], 'CREATE_PHARMACY')
            await DoubleVizitState.create_pharmacy.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=back_menu(data['lang']))
            return
        data['pharmacy'] = props[1:]
        text = translate(data['lang'], 'CREATE_COMMENT')
        await DoubleVizitState.pharmacy_comment.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id)


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=DoubleVizitState.create_pharmacy_city)
async def city_create_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                data['city'] = message.text
                text2 = translate(data['lang'], 'CHOICE_CITY')
                await DoubleVizitState.pharmacy_city.set()
                if data['mp_manager']:
                    create_city(name=data['city'], district=data['district'], token=data['token'],
                                created_by=data['mp'])
                    await message.bot.send_message(
                        text=text2, chat_id=message.chat.id,
                        reply_markup=city_all_inline(data['user_district'], token=data['token'], lang=data['lang'],
                                                     created_by=data['mp'])
                    )
                else:
                    create_city(name=data['city'], district=data['district'], token=data['token'],
                                created_by=data['user_id'])
                    await message.bot.send_message(
                        text=text2, chat_id=message.chat.id,
                        reply_markup=city_all_inline(data['user_district'], token=data['token'], lang=data['lang'],
                                                     created_by=data['user_id'])
                    )
                return
            text = translate(data['lang'], 'BACK')
            await DoubleVizitState.pharmacy_city.set()
            if data['mp_manager']:
                await message.bot.send_message(
                    text=text, chat_id=message.chat.id,
                    reply_markup=city_all_inline(data['user_district'], token=data['token'], lang=data['lang'],
                                                 created_by=data['mp'])
                )
            else:
                await message.bot.send_message(
                    text=text, chat_id=message.chat.id,
                    reply_markup=city_all_inline(data['user_district'], token=data['token'], lang=data['lang'],
                                                 created_by=data['user_id'])
                )
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=DoubleVizitState.create_pharmacy)
async def create_hospital_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                data['pharmacy_name'] = message.text
                text = translate(data['lang'], 'CREATE_ADDRESS')
                await DoubleVizitState.address.set()
                await message.bot.send_message(text=text, chat_id=message.chat.id)

                return
            text = translate(data['lang'], 'BACK')
            await DoubleVizitState.pharmacy.set()
            await message.bot.send_message(
                text=text, chat_id=message.chat.id,
                reply_markup=pharmacy_all_inline(page=data['pharmacy_page'],
                                                 token=data['token'], city=data['city'], lang=data['lang']))
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=DoubleVizitState.address)
async def create_address_pharmacy(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                Pharmacy(name=data['pharmacy_name'], city=data['city'], token=data['token'],
                         address=message.text).create()
                text = translate(data['lang'], 'SUCCESS_PHARMACY')
                await DoubleVizitState.pharmacy.set()
                await message.bot.send_message(
                    text=text, chat_id=message.chat.id,
                    reply_markup=pharmacy_all_inline(page=data['pharmacy_page'],
                                                     token=data['token'], city=data['city'], lang=data['lang']))
                return
            text = translate(data['lang'], 'CREATE_ADDRESS')
            await DoubleVizitState.address.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id)
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=DoubleVizitState.pharmacy_comment)
async def doctor_comment_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))
        ):
            if not (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))
            ):
                user = get_one_user(data['user_id'])
                name = user['first_name']
                if user['last_name']:
                    name = f"{user['first_name']} {user['last_name']}"
                data['comment'] = message.text
                doctor = Pharmacy(pharmacy_id=data['pharmacy'], token=data['token']).retrieve()
                text = f"{translate(data['lang'], 'CREATOR')}:  {name}\n{translate(data['lang'], 'PHARMACY_NAME')}:  {doctor['name']}\n{translate(data['lang'], 'COMMENT_GET')}:  {data['comment']}\n{translate(data['lang'], 'CREATED_DATE')}:  {str(datetime.now())[:19]}"
                if data['mp_manager']:
                    await DoubleVizitState.pharmacy_agreement.set()
                    await message.bot.send_message(text=text, chat_id=message.chat.id,
                                                   reply_markup=check_agreement(data['lang']))
                    return
                text = f"{translate(data['lang'], 'CREATOR')}:  {name}\n{translate(data['lang'], 'PHARMACY_NAME')}:  {doctor['name']}\n{translate(data['lang'], 'COMMENT_GET')}:  {data['comment']}\n{translate(data['lang'], 'CREATED_DATE')}:  {str(datetime.now())[:19]}"
                await DoubleVizitState.finishs.set()
                await message.bot.send_message(text=text, chat_id=message.chat.id,
                                               reply_markup=check_agreement(data['lang']))
                return
            text = translate(data['lang'], 'BACK')
            await DoubleVizitState.pharmacy.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=pharmacy_all_inline(
                city=data['city'],
                token=data['token'],
                lang=data['lang']
            ))
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.callback_query_handler(state=DoubleVizitState.pharmacy_agreement)
async def check_agreement_handler(call: types.CallbackQuery, state: FSMContext):
    props = call.data
    await call.message.delete()
    async with state.proxy() as data:
        if props == "yes":
            text = f"{translate(data['lang'], 'EVALUATION')}\n\n{translate(data['lang'], 'PREPARATION')}"
            await DoubleVizitState.pharmacy_preparation.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id, reply_markup=choice_type())
            return
        else:
            text = translate(data['lang'], 'BACK')
            await DoubleVizitState.pharmacy.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=pharmacy_all_inline(
                                                    city=data['city'],
                                                    token=data['token'],
                                                    lang=data['lang']
                                                ))


@dp.callback_query_handler(state=DoubleVizitState.pharmacy_preparation)
async def preparation_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['preparation'] = call.data[1:]
        text = translate(data['lang'], 'COMMUNICATION')
        await DoubleVizitState.pharmacy_communication.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id, reply_markup=choice_type())


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[DoubleVizitState.pharmacy_communication])
async def back_menu_begin_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = f"{translate(data['lang'], 'EVALUATION')}\n\n{translate(data['lang'], 'PREPARATION')}"
        await DoubleVizitState.pharmacy_preparation.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=choice_type())


@dp.callback_query_handler(state=DoubleVizitState.pharmacy_communication)
async def communication_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['communication'] = call.data[1:]
        text = translate(data['lang'], 'THE_NEED')
        await DoubleVizitState.pharmacy_the_need.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id, reply_markup=choice_type())


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[DoubleVizitState.pharmacy_the_need])
async def back_menu_begin_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = f"{translate(data['lang'], 'COMMUNICATION')}"
        await DoubleVizitState.pharmacy_communication.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=choice_type())


@dp.callback_query_handler(state=DoubleVizitState.pharmacy_the_need)
async def the_need_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['the_need'] = call.data[1:]
        text = translate(data['lang'], 'PRESENTATION')
        await DoubleVizitState.pharmacy_presentation.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id, reply_markup=choice_type())


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[DoubleVizitState.pharmacy_presentation])
async def back_menu_begin_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'THE_NEED')
        await DoubleVizitState.pharmacy_the_need.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=choice_type())


@dp.callback_query_handler(state=DoubleVizitState.pharmacy_presentation)
async def the_need_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['presentation'] = call.data[1:]
        text = translate(data['lang'], 'PROTEST')
        await DoubleVizitState.pharmacy_protest.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id, reply_markup=choice_type())


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[DoubleVizitState.pharmacy_protest])
async def back_menu_begin_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'PRESENTATION')
        await DoubleVizitState.pharmacy_presentation.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=choice_type())


@dp.callback_query_handler(state=DoubleVizitState.pharmacy_protest)
async def the_need_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['protest'] = call.data[1:]
        text = translate(data['lang'], 'AGREEMENT')
        await DoubleVizitState.pharmacy_agreement_.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id, reply_markup=choice_type())


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[DoubleVizitState.pharmacy_agreement_])
async def back_menu_begin_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'PROTEST')
        await DoubleVizitState.pharmacy_protest.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=choice_type())


@dp.callback_query_handler(state=DoubleVizitState.pharmacy_agreement_)
async def the_need_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['agreement'] = call.data[1:]
        text = translate(data['lang'], 'ANALYSIS')
        await DoubleVizitState.pharmacy_analysis.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id, reply_markup=choice_type())


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[DoubleVizitState.pharmacy_analysis])
async def back_menu_begin_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'AGREEMENT')
        await DoubleVizitState.pharmacy_agreement_.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=choice_type())


@dp.callback_query_handler(state=DoubleVizitState.pharmacy_analysis)
async def the_need_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['analysis'] = call.data[1:]
        mp = data.get('mp')
        if mp:
            mp = get_one_user(data['mp'])
            mp = f"{mp.get('first_name')} {mp.get('last_name')}"
        else:
            mp = "Ma'lumot yo'q"
        text = translate(data['lang'], 'SUCCESSFULLY')
        district = district_retrieve(data['user_district'])
        pharmacy = Pharmacy(pharmacy_id=data['pharmacy'], token=data['token']).retrieve()
        city = city_retrieve(data['city'], token=data['token'])
        # created_by = f"{data['first_name']} {data['last_name']}"
        user = get_one_user(data['user_id'])
        created_by = user['first_name']
        if user['last_name']:
            created_by = f"{user['first_name']} {user['last_name']}"
        if data['mp_manager']:
            create_mp_doctor_or_pharmacy_all_excel(
                created_at=str(pytz.timezone('Asia/Tashkent').localize(datetime.now()))[:19], created_by=created_by,
                village=district['name'], city=city['name'], comment=data['comment'], mp=mp,
                presentation=data['presentation'], preparation=data['preparation'],
                analysis=data['analysis'], the_need=data['the_need'],
                agreement=data['agreement'], communication=data['communication'],
                protest=data['protest'], pharmacy_name=pharmacy['name'], pharmacy_address=pharmacy['address'],
                doctor_name="No'malum", doctor_phone="No'malum", lpu="No'malum", d_type="No'malum",
                category="No'malum"
            )
            check_mp_create_pharmacy(mp=mp, city=data['city'], pharmacy=data['pharmacy'], comment=data['comment'],
                                     preparation=data['preparation'], communication=data['communication'],
                                     the_need=data['the_need'], presentation=data['presentation'],
                                     protest=data['protest'],
                                     agreement=data['agreement'], analysis=data['analysis'], token=data['token'])
        else:
            create_mp_doctor_or_pharmacy_all_excel(
                created_at=str(pytz.timezone('Asia/Tashkent').localize(datetime.now()))[:19], created_by=created_by,
                village=district['name'], city=city['name'], comment=data['comment'], mp="Ma'lumot yo'q",
                presentation=data['presentation'], preparation=data['preparation'],
                analysis=data['analysis'], the_need=data['the_need'],
                agreement=data['agreement'], communication=data['communication'],
                protest=data['protest'], pharmacy_name=pharmacy['name'], pharmacy_address=pharmacy['address'],
                doctor_name="No'malum", doctor_phone="No'malum", lpu="No'malum", d_type="No'malum",
                category="No'malum"
            )
            check_mp_create_pharmacy(mp="Ma'lumot yo'q", city=data['city'], pharmacy=data['pharmacy'],
                                     comment=data['comment'],
                                     preparation=data['preparation'], communication=data['communication'],
                                     the_need=data['the_need'], presentation=data['presentation'],
                                     protest=data['protest'],
                                     agreement=data['agreement'], analysis=data['analysis'], token=data['token'])
        await DoubleVizitState.begin.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=hospital_or_vizit(data['lang']))


@dp.callback_query_handler(state=DoubleVizitState.finishs)
async def agent_final_state_for_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'SUCCESSFULLY')
        district = district_retrieve(data['user_district'])
        pharmacy = Pharmacy(pharmacy_id=data['pharmacy'], token=data['token']).retrieve()
        city = city_retrieve(data['city'], token=data['token'])
        user = get_one_user(data['user_id'])
        created_by = user['first_name']
        if user['last_name']:
            created_by = f"{user['first_name']} {user['last_name']}"
        create_mp_doctor_or_pharmacy_all_excel(
            created_at=str(pytz.timezone('Asia/Tashkent').localize(datetime.now()))[:19], created_by=created_by,
            village=district['name'], city=city['name'], comment=data['comment'], mp="Ma'lumot yo'q",
            presentation="Ma'lumot yo'q", preparation="Ma'lumot yo'q",
            analysis="Ma'lumot yo'q", the_need="Ma'lumot yo'q",
            agreement="Ma'lumot yo'q", communication="Ma'lumot yo'q",
            protest="Ma'lumot yo'q", pharmacy_name=pharmacy['name'], pharmacy_address=pharmacy['address'],
            doctor_name="No'malum", doctor_phone="No'malum", lpu="No'malum", d_type="No'malum", category="No'malum"
        )
        check_mp_create_pharmacy(mp="Ma'lumot yo'q", city=data['city'], pharmacy=data['pharmacy'],
                                 comment=data['comment'],
                                 presentation="Ma'lumot yo'q", preparation="Ma'lumot yo'q",
                                 analysis="Ma'lumot yo'q", the_need="Ma'lumot yo'q",
                                 agreement="Ma'lumot yo'q", communication="Ma'lumot yo'q", protest="Ma'lumot yo'q",
                                 token=data['token'])
    await DoubleVizitState.begin.set()
    await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                        reply_markup=hospital_or_vizit(data['lang']))
