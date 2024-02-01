from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate, translate_cyrillic_or_latin
from api.users import district_retrieve
from api.users.users import get_one_user, update_user_data_and_phone_number
from button.inline import update_employed_menu
from dispatch import dp
from states import EmployedState, BaseState


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=EmployedState.update_phone)
async def update_admin_phone_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not message.text.startswith("+"):
            text = translate(data['lang'], 'NOT_PLUS')
            await EmployedState.update_phone.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id)
            return
        elif len(message.text) != 13:
            text = translate(data['lang'], 'NOT_LENGTH')
            await EmployedState.update_phone.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id)
            return
        try:
            int(message.text[1:])
        except Exception:
            text = translate(data['lang'], 'NOT_INT')
            await EmployedState.update_phone.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id)
            return
        member = get_one_user(data['update_member_role'])
        last_name = None
        if member.get('last_name'):
            last_name = member['last_name']
        first_name = member['first_name']
        update_user_data_and_phone_number(data['update_member_role'], first_name, last_name, message.text)
        district = district_retrieve(member['district'])
        member = get_one_user(data['update_member_role'])
        name = f"{member['first_name']}"
        if member['last_name']:
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
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=update_employed_menu(data['lang']))
