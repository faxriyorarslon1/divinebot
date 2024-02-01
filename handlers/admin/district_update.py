from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate, translate_cyrillic_or_latin
from api.users import district_retrieve
from api.users.users import update_user_is_member, update_user_district, get_one_user
from button.inline import update_employed_menu
from button.reply_markup import base_menu
from dispatch import dp
from states import EmployedState, BaseState


@dp.callback_query_handler(state=EmployedState.update_district)
async def update_admin_district_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        update_user_district(data['update_member_role'], call.data[1:])
        member = get_one_user(data['update_member_role'])
        district = district_retrieve(member['district'])
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
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=update_employed_menu(data['lang']))
