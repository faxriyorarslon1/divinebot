from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import russian, latin
from api.users.location import get_location_member
from api.users.users import get_one_user
from button.inline import village_all_inline, get_all_manager, months, get_month_day
from button.reply_markup import back_menu, admin_document
from dispatch import dp
from states import AdminDocumentState, AdminLocationState


@dp.message_handler(lambda message: (str(message.text).__eq__(russian['MANAGER_LOCATION']) or str(message.text).__eq__(
    latin['MANAGER_LOCATION']) or str(message.text).__eq__(
    translate_cyrillic_or_latin(latin['MANAGER_LOCATION'], 'cyr'))) and (
                                            not str(message.text).__eq__('/start')),
                    state=AdminDocumentState.base)
async def admin_location_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'CREATE_VILLAGE')
        text2 = translate(data['lang'], 'OR_THE_BACK')
        await AdminLocationState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
        await message.bot.send_message(text=text2, chat_id=message.chat.id,
                                       reply_markup=village_all_inline(data['lang']))


@dp.message_handler(lambda message: (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
    russian['BACK_MENU']) or message.text.__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and
                                    (not str(message.text).__eq__('/start')),
                    state=[AdminLocationState.begin])
async def settings_back_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'VIZIT_DOCUMENT_MANAGER_TEXT')
        await AdminDocumentState.base.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=admin_document(data['lang']))


@dp.callback_query_handler(state=AdminLocationState.begin)
async def admin_location_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['page'] = 1
        data['admin_district'] = call.data[1:]
        users = get_all_manager(district=call.data[1:], token=data['token'], page=data['page'], lang=data['lang'])
        if users:
            text = translate(data['lang'], 'WORKERS')
            await AdminLocationState.workers.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id, reply_markup=users)
        else:
            text = translate(data['lang'], 'NOT_FOUND')
            text2 = translate(data['lang'], 'CREATE_VILLAGE')
            await AdminLocationState.begin.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=back_menu(data['lang']))
            await call.message.bot.send_message(text=text2, chat_id=call.message.chat.id,
                                                reply_markup=village_all_inline(data['lang']))


@dp.message_handler(lambda message: (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
    russian['BACK_MENU']) or message.text.__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                                            not str(message.text).__eq__('/start')),
                    state=[AdminLocationState.workers])
async def settings_back_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'CREATE_VILLAGE')
        text2 = translate(data['lang'], 'OR_THE_BACK')
        await AdminLocationState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
        await message.bot.send_message(text=text2, chat_id=message.chat.id,
                                       reply_markup=village_all_inline(data['lang']))


@dp.callback_query_handler(state=AdminLocationState.workers)
async def workers_state_by_manager_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data.__eq__('prev'):
            data['page'] -= 1
            text = translate(data['lang'], 'WORKERS')
            await AdminLocationState.workers.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=get_all_manager(district=call.data[1:],
                                                                             token=data['token'], page=data['page'],
                                                                             lang=data['lang']))
        elif call.data.__eq__('next'):
            data['page'] += 1
            text = translate(data['lang'], 'WORKERS')
            await AdminLocationState.workers.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=get_all_manager(district=call.data[1:],
                                                                             token=data['token'], page=data['page'],
                                                                             lang=data['lang']))

        else:
            data['manager_member'] = call.data[1:]
            text = translate(data['lang'], "MONTHS_CHOICE")
            await AdminLocationState.month.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=months(data['lang']))


@dp.message_handler(lambda message: (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
    russian['BACK_MENU']) or message.text.__eq__(
    translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (not str(message.text).__eq__('/start')),
                    state=[AdminLocationState.month])
async def settings_back_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['page'] = 1
        users = get_all_manager(district=data['admin_district'], token=data['token'], page=data['page'],
                                lang=data['lang'])
        if users:
            text = translate(data['lang'], 'WORKERS')
            await AdminLocationState.workers.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=users)
        else:
            text = translate(data['lang'], 'MEMBER_NOT_FOUND')
            text2 = translate(data['lang'], 'CREATE_VILLAGE')
            await AdminLocationState.begin.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=back_menu(data['lang']))
            await message.bot.send_message(text=text2, chat_id=message.chat.id,
                                           reply_markup=village_all_inline(data['lang']))


@dp.callback_query_handler(state=AdminLocationState.month)
async def admin_manager_month_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['month'] = call.data[1:]
        text2 = translate(data['lang'], "DAY")
        await AdminLocationState.day.set()
        await call.message.bot.send_message(text=text2, chat_id=call.message.chat.id,
                                            reply_markup=get_month_day(data['month']))


@dp.message_handler(lambda message: (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
    russian['BACK_MENU']) or message.text.__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                                            not str(message.text).__eq__('/start')),
                    state=[AdminLocationState.day])
async def settings_back_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], "MONTHS_CHOICE")
        await AdminLocationState.month.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=months(data['lang']))


@dp.callback_query_handler(state=AdminLocationState.day)
async def cal_location_month_day_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        member_location = get_location_member(month=data['month'], day=call.data[1:], year=datetime.now().year,
                                              token=data['token'], user_id=data['manager_member'])
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
            await AdminLocationState.day.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=get_month_day(data['month']))
            return
        text = translate(data['lang'], "NOT_FOUND")
        await call.message.delete()
        await AdminLocationState.day.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=get_month_day(data['month']))
