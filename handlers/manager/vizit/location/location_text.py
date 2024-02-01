import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import latin, russian
from api.users.location import get_location_member, get_location_member_new
from api.users.users import get_one_user
from button.inline import get_month_day, member_list_inline, months
from button.reply_markup import base_menu, back_menu, location_menu_for_vizit, choice_bron_report
from dispatch import dp
from states import BaseState
from states.bron import VizitReportState


@dp.message_handler(lambda message: (str(message.text).__eq__(russian['VIZIT_TEXT']) or str(message.text).__eq__(
    latin['VIZIT_TEXT']) or str(message.text).__eq__(translate_cyrillic_or_latin(latin['VIZIT_TEXT'], 'cyr'))) and (
                                            not str(message.text).__eq__('/start')),
                    state=VizitReportState.location)
async def location_vizit_text_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text2 = translate(data['lang'], 'CHOICE_VIZIT')
        text = translate(data['lang'], "MONTHS_CHOICE")
        await VizitReportState.month.set()
        await message.bot.send_message(text=text2, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=months(data['lang']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[VizitReportState.month])
async def location_menu_back(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'VIZIT_LOCATION_TEXT')
        await VizitReportState.location.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=location_menu_for_vizit(data['lang']))


@dp.callback_query_handler(state=[VizitReportState.month])
async def settings_back_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data.__eq__('back'):
            text = translate(data['lang'], 'VIZIT_LOCATION_TEXT')
            await VizitReportState.location.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=location_menu_for_vizit(data['lang']))
            return
        data['month'] = call.data[1:]
        text = translate(data['lang'], "DAY")
        text2 = translate(data['lang'], 'OR_THE_BACK')
        await VizitReportState.day.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=back_menu(data['lang']))
        await call.message.bot.send_message(text=text2, chat_id=call.message.chat.id,
                                            reply_markup=get_month_day(data['month']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[VizitReportState.day])
async def location_menu_back(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'VIZIT_LOCATION_TEXT')
        await VizitReportState.location.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=location_menu_for_vizit(data['lang']))


@dp.callback_query_handler(state=VizitReportState.day)
async def cal_location_month_day_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data.__eq__('back'):
            text2 = translate(data['lang'], 'CHOICE_VIZIT')
            text = translate(data['lang'], "MONTHS_CHOICE")
            await VizitReportState.month.set()
            await call.message.bot.send_message(text=text2, chat_id=call.message.chat.id,
                                                reply_markup=back_menu(data['lang']))
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=months(data['lang']))
            return
        # represents 23:59:59
        member_location = get_location_member_new(month=data['month'], day=call.data[1:],
                                                  year=datetime.datetime.now().year,
                                                  token=data['token'], user_id=data['location_member_id'])
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        text = translate(data['lang'], "LOCATION_USER")
        if member_location:
            for i in member_location:
                await call.message.bot.send_message(
                    text=f"{translate(data['lang'], 'CREATED_DATE')}: {i['created_at'][:10]} {i['created_at'][11:19]}",
                    chat_id=call.message.chat.id)
                await call.message.bot.send_location(chat_id=call.message.chat.id, latitude=i['lat'],
                                                     longitude=i['lan'])
            user = get_one_user(data['user_id'])
            data['role'] = user['role']
            await VizitReportState.day.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=get_month_day(data['month']))
            return
        text = translate(data['lang'], "NOT_FOUND")
        await call.message.delete()
        await VizitReportState.day.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=get_month_day(data['month']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[VizitReportState.day])
async def location_menu_back(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'VIZIT_LOCATION_TEXT')
        await VizitReportState.month.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=choice_bron_report(data['lang']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[VizitReportState.location])
async def location_menu_back(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], "MEMBER_LIST")
        text2 = translate(data['lang'], 'OR_THE_BACK')
        member = member_list_inline(data['lang'], data['district'])
        if member:
            await VizitReportState.member_list.set()
            await message.bot.send_message(text=text2, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=member)
