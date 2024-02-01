from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.translate_language import latin, russian
from Tranlate.tranlate_config import translate, translate_cyrillic_or_latin
from api.users.users import get_one_user
from button.inline import language_choice
from button.reply_markup import settings_menu, base_menu, back_menu
from dispatch import dp
from states import BaseState, DeliveryState, SupplierState
from states.settings import SettingState


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['SETTINGS']) or str(message.text).__eq__(
        russian['SETTINGS']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['SETTINGS'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')), state=BaseState.base)
async def settings_menu_for_user(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'SETTINGS_MENU')
        await SettingState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=settings_menu(data['lang']))


@dp.message_handler(lambda message: (str(message.text).__eq__(latin['LANGUAGE_BUTTON']) or str(message.text).__eq__(
    russian['LANGUAGE_BUTTON']) or str(message.text).__eq__(
    translate_cyrillic_or_latin(latin['LANGUAGE_BUTTON'], 'cyr'))) and (not str(message.text).__eq__('/start')),
                    state=SettingState.begin)
async def language_update_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text2 = translate(data['lang'], 'OR_THE_BACK')
        text = translate(data['lang'], 'LANGUAGE')
        await SettingState.language.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
        await message.bot.send_message(text=text2, chat_id=message.chat.id, reply_markup=language_choice(data['lang']))


@dp.message_handler(lambda message: (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
    russian['BACK_MENU']) or message.text.__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                                    not str(message.text).__eq__('/start')),
                    state=[SettingState.begin, SettingState.language, DeliveryState.begin, DeliveryState.submit,
                           DeliveryState.reply_products, DeliveryState.bron, SupplierState.begin, SupplierState.submit])
async def settings_back_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(lang=data['lang'], text='BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.callback_query_handler(state=SettingState.language)
async def edit_language_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['lang'] = call.data
        text = translate(data['lang'], 'SUCCESS_UPDATED')
        await SettingState.begin.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=settings_menu(data['lang']))
