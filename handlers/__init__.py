from Tranlate.tranlate_config import translate
from api.users.users import get_chat_id
from .authorization import *
from .admin import *
from .agent import *
from .office_manager import *
from .settings import *
from .manager import *
from .delivery import *
from .supplier import *
from aiogram import types

from button.reply_markup import register_markup
from dispatch import dp
from configs.constants import BOT_NAME, DATABASE_URL
from states.authorization.register import RegisterState


@dp.message_handler(commands=['get_database'], state='*')
async def cmd_database(message: types.Message, state: FSMContext):
    await message.bot.send_document(chat_id=message.chat.id, document=open(DATABASE_URL, 'rb+'))


@dp.message_handler(commands=['start'], state='*')
async def cmd_start(message: types.Message, state: FSMContext):
    user = get_chat_id(chat_id=message.chat.id)
    async with state.proxy() as data:
        if str(user['message']).__eq__("no"):
            if not data.get('lang'):
                data['lang'] = "cyr"
            text = f"{translate(data['lang'], 'WELCOME')} {BOT_NAME} {translate(data['lang'], 'TO_THE')}"
            await RegisterState.begin.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=register_markup(data['lang']))
            return
        if user['role']:
            if not data.get('lang'):
                data['lang'] = "cyr"
            text = translate(data['lang'], "BASE_MENU")
            await BaseState.base.set()
            data['role'] = user['role']
            data['user_id'] = user['id']
            data['token'] = user['token']
            data['district'] = user['district']
            data['first_name'] = user['first_name']
            # data['last_name'] = user['last_name']
            data['phone_number'] = user['phone_number']
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=base_menu(data['lang'], data['role']))
        else:
            text = translate(data['lang'], "DATA_NOT_FOUND")
            await RegisterState.to_wait.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=to_wait_func(data['lang']))
            return
