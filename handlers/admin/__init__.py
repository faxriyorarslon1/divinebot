from .test_excel import *
from .employee_data import *
from .employee_phone import *
from .district_update import *
from .admin_location import *
from .vizit_report import *
from .apteka_residue import *
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import latin, russian
from api.users import district_retrieve
from api.users.users import get_one_user, update_user_is_member, delete_user
from button.inline import role_member, get_all_not_active_inline, get_all_user_member, role_choice, check_basket, \
    update_employed_menu, village_all_inline
from button.reply_markup import base_menu
from dispatch import dp
from states import BaseState, EmployedState, NewEmployedState


@dp.message_handler(
    lambda message: str(message.text).__eq__(latin['EMPLOYED']) or str(message.text).__eq__(russian['EMPLOYED']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['EMPLOYED'], 'cyr')), state=BaseState.base)
async def admin_employed_menu_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], "EMPLOYED_MENU")
        text2 = translate(data['lang'], 'OR_THE_BACK')
        await EmployedState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=ReplyKeyboardRemove())
        await message.bot.send_message(text=text2, chat_id=message.chat.id, reply_markup=role_member(data['lang']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['NEW_EMPLOYED']) or str(message.text).__eq__(
        russian['NEW_EMPLOYED']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['NEW_EMPLOYED'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')), state=BaseState.base)
async def admin_employed_menu_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], "NEW_EMPLOYED_MENU")
        text2 = translate(data['lang'], 'OR_THE_BACK')
        await NewEmployedState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=ReplyKeyboardRemove())
        await message.bot.send_message(text=text2, chat_id=message.chat.id,
                                       reply_markup=get_all_not_active_inline(data['lang']))


@dp.callback_query_handler(state=EmployedState.begin)
async def user_back_or_choice_employed_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data.__eq__('back'):
            text = translate(data['lang'], 'BACK')
            await BaseState.base.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=base_menu(data['lang'], data['role']))
        else:
            roles = get_all_user_member(data['lang'], call.data)
            if roles:
                text = translate(data['lang'], 'ROLES_MEMBER')
                await EmployedState.member.set()
                await call.message.bot.send_message(text=text, chat_id=call.message.chat.id, reply_markup=roles)
            else:
                text = translate(data['lang'], "MEMBER_NOT_FOUND")
                await BaseState.base.set()
                await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                    reply_markup=base_menu(data['lang'], data['role']))


@dp.callback_query_handler(state=EmployedState.member)
async def user_role_member_all_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data.__eq__('back'):
            text = translate(data['lang'], 'BACK')
            await BaseState.base.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=base_menu(data['lang'], data['role']))
        else:
            data['update_member_role'] = call.data[1:]
            member = get_one_user(call.data[1:])
            district = district_retrieve(member['district'])
            name = f"{member['first_name']}"
            if member.get('last_name'):
                name = f"{member['first_name']} {member['last_name']}"
            data['member_role'] = member['role']
            phone = member['phone_number']
            role = ""
            if member.get('role') == 'manager':
                role = translate_cyrillic_or_latin('Meneger', data['lang'])
            elif member.get('role') == 'agent':
                role = translate_cyrillic_or_latin('Tibbiy vakil', data['lang'])
            elif member.get('role') == 'delivery':
                role = translate_cyrillic_or_latin('Omborxona Meneger', data['lang'])
            elif member.get('role') == 'office_manager':
                role = translate_cyrillic_or_latin('Office Meneger', data['lang'])
            elif member.get('role') == "supplier":
                role = translate_cyrillic_or_latin('Yetkazib beruvchi', data['lang'])
            text = f"{translate(data['lang'], 'NAME_MEMBER')}: {translate_cyrillic_or_latin(name, data['lang'])}\n{translate(data['lang'], 'MEMBER_PHONE')}: {phone}\n{translate(data['lang'], 'DISTRICT')}: {translate_cyrillic_or_latin(district.get('name'), data['lang'])}\n{translate(data['lang'], 'ROLE')}: {role}"
            await EmployedState.update.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=update_employed_menu(data['lang']))


@dp.callback_query_handler(state=EmployedState.update)
async def update_user_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data.__eq__('back'):
            text = translate(data['lang'], 'BACK')
            await BaseState.base.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=base_menu(data['lang'], data['role']))
        elif call.data.__eq__('update_role'):
            text = translate(data['lang'], 'CHOICE_ROLE')
            await EmployedState.update_role.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=role_member(data['lang']))
        elif call.data.__eq__('update_district'):
            text = translate(data['lang'], 'VILLAGE')
            await EmployedState.update_district.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=village_all_inline(data['lang']))
        elif call.data.__eq__('update_phone_number'):
            text = translate(data['lang'], 'CREATE_USER_PHONE_NUMBER')
            await EmployedState.update_phone.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id)
        elif call.data.__eq__('update_user_data'):
            text = translate(data['lang'], 'CREATE_USER_NAME')
            await EmployedState.update_name.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id)
        elif call.data.__eq__('update_user_data_last_name'):
            text = translate(data['lang'], 'CREATE_USER_LAST_NAME')
            await EmployedState.update_last_name.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id)

        else:
            text = translate(data['lang'], 'DELETE_MEMBER_CHECK')
            await EmployedState.delete_user.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=check_basket(data['lang']))


@dp.callback_query_handler(state=EmployedState.update_role)
async def update_role_user_for_checked_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data.__eq__('back'):
            text = translate(data['lang'], 'NO_SUCCESS')
            await BaseState.base.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=base_menu(data['lang'], data['role']))
        else:
            data['is_member_role'] = call.data
            text = translate(data['lang'], 'PENDING_UPDATE')
            await EmployedState.finished.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=check_basket(data['lang']))


@dp.callback_query_handler(state=EmployedState.delete_user)
async def delete_user_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data.__eq__('no'):
            text = translate(data['lang'], 'NO_SUCCESS')
            await BaseState.base.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=base_menu(data['lang'], data['role']))
        else:
            delete_user(data['update_member_role'])
            text = translate(data['lang'], 'SUCCESS_DELETED')
            await BaseState.base.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=base_menu(data['lang'], data['role']))


@dp.callback_query_handler(state=EmployedState.finished)
async def update_member_finished_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data.__eq__('no'):
            text = translate(data['lang'], 'NO_SUCCESS')
            await BaseState.base.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=base_menu(data['lang'], data['role']))
        else:
            update_user_is_member(data['update_member_role'], data['is_member_role'])
            text = translate(data['lang'], 'SUCCESS')
            await BaseState.base.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=base_menu(data['lang'], data['role']))


@dp.callback_query_handler(state=EmployedState.delete_user)
async def update_member_finished_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data.__eq__('no'):
            text = translate(data['lang'], 'NO_SUCCESS')
            await BaseState.base.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=base_menu(data['lang'], data['role']))
        else:
            update_user_is_member(data['update_member_role'], data['is_member_role'])
            text = translate(data['lang'], 'SUCCESS')
            user = get_one_user(data['user_id'])
            data['role'] = user['role']
            await BaseState.base.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=base_menu(data['lang'], data['role']))


@dp.callback_query_handler(state=NewEmployedState.begin)
async def user_back_or_choice_document_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data.__eq__('back'):
            text = translate(data['lang'], 'BACK')
            await BaseState.base.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=base_menu(data['lang'], data['role']))
        else:
            member = get_one_user(call.data[1:])
            data['updated_member'] = call.data[1:]
            district = district_retrieve(member['district'])
            name = f"{member['first_name']}"
            if member.get('last_name'):
                name = f"{member['first_name']} {member['last_name']}"
            phone = member['phone_number']
            text = f"{translate(data['lang'], 'NAME_MEMBER')}: {translate_cyrillic_or_latin(name, data['lang'])}\n{translate(data['lang'], 'MEMBER_PHONE')}: {phone}\n{translate(data['lang'], 'DISTRICT')}:{translate_cyrillic_or_latin(district.get('name'), data['lang'])}"
            await NewEmployedState.new.set()
            await call.message.bot.send_photo(chat_id=call.message.chat.id, caption=text,
                                              reply_markup=role_choice(data['lang']),
                                              photo=member.get('passport_image_path'))
            return


@dp.callback_query_handler(state=NewEmployedState.new)
async def user_passport_image_path(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data.__eq__('back'):
            text = translate(data['lang'], 'BACK')
            await BaseState.base.set()
            user = get_one_user(data['user_id'])
            data['role'] = user['role']
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=base_menu(data['lang'], data['role']))
        else:
            text = translate(data['lang'], 'CHOICE_ROLE')
            await NewEmployedState.update_role.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=role_member(data['lang']))


@dp.callback_query_handler(state=NewEmployedState.update_role)
async def check_update_or_un_update_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data.__eq__('back'):
            text = translate(data['lang'], 'NO_SUCCESS')
            await BaseState.base.set()
            user = get_one_user(data['user_id'])
            data['role'] = user['role']
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=base_menu(data['lang'], data['role']))
        else:
            data['is_member_role'] = call.data
            text = translate(data['lang'], 'PENDING_UPDATE')
            await NewEmployedState.pending.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=check_basket(data['lang']))


@dp.callback_query_handler(state=NewEmployedState.pending)
async def check_basked_update_user_finished_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data.__eq__('no'):
            text = translate(data['lang'], 'NO_SUCCESS')
            await BaseState.base.set()
            user = get_one_user(data['user_id'])
            data['role'] = user['role']
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=base_menu(data['lang'], data['role']))
        else:
            text = translate(data['lang'], 'SUCCESS')
            update_user_is_member(data['updated_member'], data['is_member_role'])
            await BaseState.base.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=base_menu(data['lang'], data['role']))

#
# @dp.message_handler(lambda message: str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
#     russian['BACK_MENU']) or str(message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr')),
#                     state=[.bron, CreateBronState.count, CreateBronState.inn, CreateBronState.comment,
#                            CreateBronState.check, CreateBronState.products, CreateBronState.reply_products])
# async def back_manu_handler(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         text = translate(data['lang'], "BASE_MENU_BACK")
#         await BaseState.base.set()
#         user = get_one_user(data['user_id'])
#         data['role'] = user['role']
#         await message.bot.send_message(text=text, chat_id=message.chat.id,
#                                        reply_markup=base_menu(data['lang'], data['role']))
