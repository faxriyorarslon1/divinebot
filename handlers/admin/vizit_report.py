from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import latin, russian
from api.users import district_retrieve
from api.users.location import get_location_member
from api.users.users import get_one_user
from button.inline import months, member_list_inline, village_all_inline, get_month_day
from button.reply_markup import back_menu, choice_bron_report, location_menu_for_vizit, base_menu
from dispatch import dp
from excel_utils import check_excel
from excel_utils.vizit import VIZIT_EXCEL_PATH
from states import BaseState
from states.bron import VizitReportState, AdminVizitReportState


@dp.message_handler(lambda message: (str(message.text).__eq__(latin["ADMIN_VIZIT_REPORT"]) or str(message.text).__eq__(
    russian["ADMIN_VIZIT_REPORT"]) or str(message.text).__eq__(
    translate_cyrillic_or_latin(latin["ADMIN_VIZIT_REPORT"], 'cyr'))) and (not str(message.text).__eq__('/start')),
                    state=BaseState.base)
async def bron_report_begin_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text2 = translate(data['lang'], 'CHOICE_VIZIT')
        text = translate(data['lang'], "VIZIT_REPORT_MESSAGE")
        await AdminVizitReportState.begin.set()
        await message.bot.send_message(text=text2, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=village_all_inline(data['lang']))


@dp.callback_query_handler(state=AdminVizitReportState.begin)
async def vizit_district_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['village'] = call.data[1:]
        text = translate(data['lang'], 'ADMIN_CREATE_VILLAGE')
        await AdminVizitReportState.village.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=choice_bron_report(data['lang']))


@dp.message_handler(lambda message: (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
    russian['BACK_MENU']) or message.text.__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                                            not str(message.text).__eq__('/start')),
                    state=[AdminVizitReportState.begin])
async def settings_back_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(lambda message: (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
    russian['BACK_MENU']) or message.text.__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                                            not str(message.text).__eq__('/start')),
                    state=[AdminVizitReportState.village])
async def settings_back_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text2 = translate(data['lang'], 'CHOICE_VIZIT')
        text = translate(data['lang'], "VIZIT_REPORT_MESSAGE")
        await AdminVizitReportState.begin.set()
        await message.bot.send_message(text=text2, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=village_all_inline(data['lang']))


#
#
# @dp.message_handler(lambda message: (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
#     russian['BACK_MENU']) or message.text.__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
#                                             not str(message.text).__eq__('/start')),
#                     state=[AdminVizitReportState.village])
# async def settings_back_handler(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         text2 = translate(data['lang'], 'CHOICE_VIZIT')
#         text = translate(data['lang'], "MONTHS_CHOICE")
#         await AdminVizitReportState.month.set()
#         await message.bot.send_message(text=text2, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
#         await message.bot.send_message(text=text, chat_id=message.chat.id,
#                                        reply_markup=village_all_inline(data['lang']))


@dp.message_handler(lambda message: (str(message.text).__eq__(russian['DOCUMENT_FILE']) or str(message.text).__eq__(
    latin['DOCUMENT_FILE']) or str(message.text).__eq__(
    translate_cyrillic_or_latin(latin['DOCUMENT_FILE'], 'cyr'))) and (not str(message.text).__eq__('/start')),
                    state=AdminVizitReportState.village)
async def create_document_file(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        district = district_retrieve(data['village'])
        excel_path = f"obshi_vizit_excel_{district['name']}.xlsx"
        from os.path import join as join_path
        check = check_excel(VIZIT_EXCEL_PATH, excel_path)
        if check.__eq__('bosingiz'):
            document = join_path(VIZIT_EXCEL_PATH, excel_path)
            await AdminVizitReportState.village.set()
            await message.bot.send_document(chat_id=message.chat.id, document=open(document, 'rb+'),
                                            reply_markup=choice_bron_report(data['lang']))
            return
        text = translate(data['lang'], "NOT_FOUND")
        await AdminVizitReportState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=choice_bron_report(data['lang']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['GEOLOCATION_DOCUMENT']) or str(message.text).__eq__(
        russian['GEOLOCATION_DOCUMENT']) or str(message.text).__eq__(
        translate_cyrillic_or_latin(latin['GEOLOCATION_DOCUMENT'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')), state=AdminVizitReportState.village)
async def location_message_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], "MEMBER_LIST")
        text2 = translate(data['lang'], 'OR_THE_BACK')
        member = member_list_inline(data['lang'], data['village'])
        if member:
            await AdminVizitReportState.member_list.set()
            await message.bot.send_message(text=text2, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=member)
            return
        text = translate(data['lang'], 'MEMBER_NOT_FOUND')
        await AdminVizitReportState.month.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=village_all_inline(data['lang']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[AdminVizitReportState.member_list])
async def location_menu_back(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'ADMIN_CREATE_VILLAGE')
        await AdminVizitReportState.village.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=choice_bron_report(data['lang']))


@dp.callback_query_handler(state=AdminVizitReportState.member_list)
async def cal_member_document_or_text_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['location_member_id'] = call.data[1:]
        text = translate(data['lang'], 'VIZIT_LOCATION_TEXT')
        await AdminVizitReportState.location.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=location_menu_for_vizit(data['lang']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[AdminVizitReportState.month])
async def location_menu_back(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'VIZIT_LOCATION_TEXT')
        await AdminVizitReportState.location.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=location_menu_for_vizit(data['lang']))


@dp.message_handler(lambda message: (str(message.text).__eq__(russian['VIZIT_TEXT']) or str(message.text).__eq__(
    latin['VIZIT_TEXT']) or str(message.text).__eq__(translate_cyrillic_or_latin(latin['VIZIT_TEXT'], 'cyr'))) and (
                                            not str(message.text).__eq__('/start')),
                    state=AdminVizitReportState.location)
async def location_vizit_text_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text2 = translate(data['lang'], 'CHOICE_VIZIT')
        text = translate(data['lang'], "MONTHS_CHOICE")
        await AdminVizitReportState.month.set()
        await message.bot.send_message(text=text2, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=months(data['lang']))


@dp.callback_query_handler(state=[AdminVizitReportState.month])
async def settings_back_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data.__eq__('back'):
            text = translate(data['lang'], 'VIZIT_LOCATION_TEXT')
            await AdminVizitReportState.location.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=location_menu_for_vizit(data['lang']))
            return
        data['month'] = call.data[1:]
        text = translate(data['lang'], "DAY")
        text2 = translate(data['lang'], 'OR_THE_BACK')
        await AdminVizitReportState.day.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=back_menu(data['lang']))
        await call.message.bot.send_message(text=text2, chat_id=call.message.chat.id,
                                            reply_markup=get_month_day(data['month']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[AdminVizitReportState.day])
async def location_menu_back(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text2 = translate(data['lang'], 'CHOICE_VIZIT')
        text = translate(data['lang'], "MONTHS_CHOICE")
        await AdminVizitReportState.month.set()
        await message.bot.send_message(text=text2, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=months(data['lang']))


@dp.callback_query_handler(state=AdminVizitReportState.day)
async def cal_location_month_day_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        member_location = get_location_member(month=data['month'], day=call.data[1:], year=datetime.now().year,
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
            await AdminVizitReportState.day.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=get_month_day(data['month']))
            return
        text = translate(data['lang'], "NOT_FOUND")
        await call.message.delete()
        await AdminVizitReportState.day.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=get_month_day(data['month']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[AdminVizitReportState.day])
async def location_menu_back(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'VIZIT_LOCATION_TEXT')
        await AdminVizitReportState.month.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=choice_bron_report(data['lang']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[AdminVizitReportState.location])
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
