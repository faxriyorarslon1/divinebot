from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate, translate_cyrillic_or_latin
from api.users import district_retrieve
from api.users.users import update_user_is_member, update_user_district, get_one_user, update_user_data_and_phone_number
from button.inline import update_employed_menu
from button.reply_markup import base_menu
from dispatch import dp
from states import EmployedState, BaseState


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=EmployedState.update_name)
async def update_admin_first_name_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['employee_name'] = message.text
        member = get_one_user(data['update_member_role'])
        phone_number = member['phone_number']
        update_user_data_and_phone_number(data['update_member_role'], data['employee_name'], member.get('last_name'),
                                          phone_number)
        district = district_retrieve(member['district'])
        member = get_one_user(data['update_member_role'])
        name = f"{member['first_name']}"
        if member.get('last_name'):
            name = f"{member['first_name']} {member['last_name']}"
        data['member_role'] = member['role']
        phone = member['phone_number']
        role = ""
        if member.get('role') == 'manager':
            role = translate_cyrillic_or_latin('Menedjer', data['lang'])
        elif member.get('role') == 'agent':
            role = translate_cyrillic_or_latin('Tibbiy vakil', data['lang'])
        elif member.get('role') == 'delivery':
            role = translate_cyrillic_or_latin('Omborxona Menedjer', data['lang'])
        elif member.get('role') == 'office_manager':
            role = translate_cyrillic_or_latin('Offis Menedjer', data['lang'])
        elif member.get('role') == "supplier":
            role = translate_cyrillic_or_latin('Yetkazib beruvchi', data['lang'])
        text = f"{translate(data['lang'], 'NAME_MEMBER')}: {translate_cyrillic_or_latin(name, data['lang'])}\n{translate(data['lang'], 'MEMBER_PHONE')}: {phone}\n{translate(data['lang'], 'DISTRICT')}: {translate_cyrillic_or_latin(district.get('name'), data['lang'])}\n{translate(data['lang'], 'ROLE')}: {role}"
        await EmployedState.update.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=update_employed_menu(data['lang']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=EmployedState.update_last_name)
async def update_user_admin_last_name_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        member = get_one_user(data['update_member_role'])
        phone_number = member['phone_number']
        update_user_data_and_phone_number(data['update_member_role'], member.get('first_name'), message.text,
                                          phone_number)
        district = district_retrieve(member['district'])
        member = get_one_user(data['update_member_role'])
        name = f"{member['first_name']}"
        if member.get('last_name'):
            name = f"{member['first_name']} {member['last_name']}"
        data['member_role'] = member['role']
        phone = member['phone_number']
        role = ""
        if member.get('role') == 'manager':
            role = translate_cyrillic_or_latin('Menedjer', data['lang'])
        elif member.get('role') == 'agent':
            role = translate_cyrillic_or_latin('Tibbiy vakil', data['lang'])
        elif member.get('role') == 'delivery':
            role = translate_cyrillic_or_latin('Omborxona Menedjer', data['lang'])
        elif member.get('role') == 'office_manager':
            role = translate_cyrillic_or_latin('Offis Menedjer', data['lang'])
        elif member.get('role') == "supplier":
            role = translate_cyrillic_or_latin('Yetkazib beruvchi', data['lang'])
        text = f"{translate(data['lang'], 'NAME_MEMBER')}: {translate_cyrillic_or_latin(name, data['lang'])}\n{translate(data['lang'], 'MEMBER_PHONE')}: {phone}\n{translate(data['lang'], 'DISTRICT')}: {translate_cyrillic_or_latin(district.get('name'), data['lang'])}\n{translate(data['lang'], 'ROLE')}: {role}"
        await EmployedState.update.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=update_employed_menu(data['lang']))

# @dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=EmployedState.update_name)
# async def update_admin_first_name_handler(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['employee_name'] = message.text
#         member = get_one_user(data['update_member_role'])
#         phone_number = member['phone_number']
#         update_user_data_and_phone_number(data['update_member_role'], data['employee_name'], member.get('last_name'),
#                                           phone_number)
#         district = district_retrieve(member['district'])
#         member = get_one_user(data['update_member_role'])
#         name = f"{member['first_name']}"
#         if member.get('last_name'):
#             name = f"{member['first_name']} {member['last_name']}"
#         data['member_role'] = member['role']
#         phone = member['phone_number']
#         role = ""
#         if member.get('role') == 'manager':
#             role = translate_cyrillic_or_latin('Meneger', data['lang'])
#         elif member.get('role') == 'agent':
#             role = translate_cyrillic_or_latin('Tibbiy vakil', data['lang'])
#         elif member.get('role') == 'delivery':
#             role = translate_cyrillic_or_latin('Omborxona Meneger', data['lang'])
#         elif member.get('role') == 'office_manager':
#             role = translate_cyrillic_or_latin('Office Meneger', data['lang'])
#         elif member.get('role') == "supplier":
#             role = translate_cyrillic_or_latin('Yetkazib beruvchi', data['lang'])
#         text = f"{translate(data['lang'], 'NAME_MEMBER')}: {translate_cyrillic_or_latin(name, data['lang'])}\n{translate(data['lang'], 'MEMBER_PHONE')}: {phone}\n{translate(data['lang'], 'DISTRICT')}: {translate_cyrillic_or_latin(district.get('name'), data['lang'])}\n{translate(data['lang'], 'ROLE')}: {role}"
#         await EmployedState.update.set()
#         await message.bot.send_message(text=text, chat_id=message.chat.id,
#                                        reply_markup=update_employed_menu(data['lang']))
#
#
# @dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=EmployedState.update_last_name)
# async def update_user_admin_last_name_handler(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         member = get_one_user(data['update_member_role'])
#         phone_number = member['phone_number']
#         update_user_data_and_phone_number(data['update_member_role'], data['employee_name'], message.text, phone_number)
#         district = district_retrieve(member['district'])
#         member = get_one_user(data['update_member_role'])
#         name = f"{member['first_name']}"
#         if member.get('last_name'):
#             name = f"{member['first_name']} {member['last_name']}"
#         data['member_role'] = member['role']
#         phone = member['phone_number']
#         role = ""
#         if member.get('role') == 'manager':
#             role = translate_cyrillic_or_latin('Meneger', data['lang'])
#         elif member.get('role') == 'agent':
#             role = translate_cyrillic_or_latin('Tibbiy vakil', data['lang'])
#         elif member.get('role') == 'delivery':
#             role = translate_cyrillic_or_latin('Omborxona Meneger', data['lang'])
#         elif member.get('role') == 'office_manager':
#             role = translate_cyrillic_or_latin('Office Meneger', data['lang'])
#         elif member.get('role') == "supplier":
#             role = translate_cyrillic_or_latin('Yetkazib beruvchi', data['lang'])
#         text = f"{translate(data['lang'], 'NAME_MEMBER')}: {translate_cyrillic_or_latin(name, data['lang'])}\n{translate(data['lang'], 'MEMBER_PHONE')}: {phone}\n{translate(data['lang'], 'DISTRICT')}: {translate_cyrillic_or_latin(district.get('name'), data['lang'])}\n{translate(data['lang'], 'ROLE')}: {role}"
#         await EmployedState.update.set()
#         await message.bot.send_message(text=text, chat_id=message.chat.id,
#                                        reply_markup=update_employed_menu(data['lang']))
