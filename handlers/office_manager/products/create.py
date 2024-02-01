import requests
from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import latin, russian
from api.product import create_product
from api.users.users import get_one_user
from button.inline import status
from button.reply_markup import base_menu, back_menu, crud_for_office_manager
from configs.constants import BOT_TOKEN
from dispatch import dp, bot
from excel_utils.product_report import create_product_image
from states import BaseState
from states.orders import OrdersState, CreateProductState


@dp.message_handler(lambda message: (str(message.text).__eq__(russian['CREATE_PRODUCT']) or str(message.text).__eq__(
    latin['CREATE_PRODUCT']) or str(message.text).__eq__(
    translate_cyrillic_or_latin(latin['CREATE_PRODUCT'], 'cyr'))) and (not str(message.text).__eq__('/start')),
                    state=OrdersState.begin)
async def create_product_name_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'CREATE_PRODUCT_NAME')
        await CreateProductState.name.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=CreateProductState.name)
async def create_content_product_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                data['create_product_name'] = message.text
                text = translate(data['lang'], 'CREATE_PRODUCT_CONTENT')
                await CreateProductState.content.set()
                await message.bot.send_message(text=text, chat_id=message.chat.id)
                return
            text = translate(data['lang'], 'THE_BACK')
            await OrdersState.begin.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=crud_for_office_manager(data['lang']))
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=CreateProductState.content)
async def create_product_price_50(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                data['create_product_content'] = message.text
                text = translate(data['lang'], 'CREATE_PRODUCT_PRICE50%')
                await CreateProductState.price50.set()
                await message.bot.send_message(text=text, chat_id=message.chat.id)
                return
            text = translate(data['lang'], 'THE_BACK')
            await OrdersState.begin.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=crud_for_office_manager(data['lang']))
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=CreateProductState.price50)
async def create_product_price_100(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                try:
                    float(message.text)
                    data['create_product_price50'] = float(message.text)
                except Exception:
                    await message.delete()
                    return
                text = translate(data['lang'], 'CREATE_PRODUCT_PRICE100%')
                await CreateProductState.price100.set()
                await message.bot.send_message(text=text, chat_id=message.chat.id)
                return
            text = translate(data['lang'], 'THE_BACK')
            await OrdersState.begin.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=crud_for_office_manager(data['lang']))
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=CreateProductState.price100)
async def create_product_original_count(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                try:
                    float(message.text)
                    data['create_product_price100'] = float(message.text)
                except Exception:
                    await message.delete()
                    return
                text = translate(data['lang'], 'CREATE_PRODUCT_ORIGINAL_COUNT')
                await CreateProductState.original_count.set()
                await message.bot.send_message(text=text, chat_id=message.chat.id)
                return
            text = translate(data['lang'], 'THE_BACK')
            await OrdersState.begin.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=crud_for_office_manager(data['lang']))
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=CreateProductState.original_count)
async def create_product_expiration_date(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                data['create_product_original_count'] = message.text
                text = translate(data['lang'], 'CREATE_PRODUCT_EXPIRATION_DATE')
                await CreateProductState.expiration_date.set()
                await message.bot.send_message(text=text, chat_id=message.chat.id)
                return
            text = translate(data['lang'], 'THE_BACK')
            await OrdersState.begin.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=crud_for_office_manager(data['lang']))
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=CreateProductState.expiration_date)
async def create_product_seria_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                if len(message.text) != 10:
                    await message.delete()
                    return
                try:
                    int(message.text[:4]) and int(message.text[5:7]) and int(message.text[8:])
                except Exception:
                    await message.delete()
                    return
                data['create_product_expiration_date'] = message.text
                text = translate(data['lang'], "CREATE_PRODUCT_SERIA")
                await CreateProductState.seria.set()
                await message.bot.send_message(text=text, chat_id=message.chat.id)
                return
            text = translate(data['lang'], 'THE_BACK')
            await OrdersState.begin.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=crud_for_office_manager(data['lang']))
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=CreateProductState.seria)
async def create_product_status(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                data['create_product_seria'] = message.text
                await CreateProductState.status.set()
                text = translate(data['lang'], "CREATE_PRODUCT_STATUS")
                await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=status(data['lang']))
                return
            text = translate(data['lang'], 'THE_BACK')
            await OrdersState.begin.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=crud_for_office_manager(data['lang']))
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.callback_query_handler(state=CreateProductState.states)
async def create_product_status(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if not (call.message.text.__eq__(latin['BACK_MENU']) or call.message.text.__eq__(
                russian['BACK_MENU']) or call.message.text.__eq__(
            translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
            if call.data.__eq__("active"):
                data['create_product_status'] = True
            else:
                data['create_product_status'] = False
            text = translate(data['lang'], 'CREATE_PRODUCT_THE_REST')
            await CreateProductState.the_rest.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id)
            return
        text = translate(data['lang'], 'THE_BACK')
        await OrdersState.begin.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=crud_for_office_manager(data['lang']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[CreateProductState.status])
async def create_product_back_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'THE_BACK')
        await OrdersState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=crud_for_office_manager(data['lang']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=CreateProductState.the_rest)
async def create_product_the_rest_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                data['create_product_the_rest'] = message.text
                text = translate(data['lang'], 'CREATE_PRODUCT_IMAGE')
                await CreateProductState.product_image.set()
                await message.bot.send_message(text=text, chat_id=message.chat.id)
                return
            text = translate(data['lang'], 'THE_BACK')
            await OrdersState.begin.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=crud_for_office_manager(data['lang']))
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), content_types=types.ContentType.PHOTO,
                    state=CreateProductState.product_image)
async def create_product_image_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['product_image'] = message.photo[-1].file_id
        text = translate(data['lang'], 'SUCCESSFULLY')
        create_product(name=data['create_product_name'], composition=data['create_product_content'],
                       count=data['create_product_the_rest'],
                       original_count=data['create_product_original_count'],
                       price1=data['create_product_price50'], price2=data['create_product_price100'],
                       expired_date=data['create_product_expiration_date'], seria=data['create_product_seria'],
                       active=data['create_product_status'], image=str(data['product_image']),
                       token=data['token'])
        file = await bot.get_file(data['product_image'])
        file_pah = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"
        response = requests.get(file_pah)
        create_product_image(data['product_image'], response.content, file_pah)
        await OrdersState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=crud_for_office_manager(data['lang']))
        return
