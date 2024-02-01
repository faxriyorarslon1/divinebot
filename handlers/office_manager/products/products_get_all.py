from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import latin, russian
from api.product import get_one_product
from api.users.users import get_one_user
from button.inline import office_manager_all_product_inline, choice_office_manager, how_to_edit_for_product, \
    check_basket
from button.reply_markup import back_menu, base_menu, crud_for_office_manager
from dispatch import dp
from excel_utils.product_report import PRODUCT_IMAGE
from states import BaseState
from states.orders import OrdersState, GetAllProductState
from utils.number_split_for_price import price_split


@dp.message_handler(lambda message: str(message.text).__eq__(latin['GET_ALL_PRODUCT']) or str(message.text).__eq__(
    russian['GET_ALL_PRODUCT']) or str(message.text).__eq__(
    translate_cyrillic_or_latin(latin['GET_ALL_PRODUCT'], 'cyr')), state=OrdersState.begin)
async def get_all_products_for_office_manager_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['page_office_manager'] = 1
        text = translate(data['lang'], 'GET_ALL_PRODUCT_TEXT')
        text2 = translate(data['lang'], 'OR_THE_BACK')
        product = office_manager_all_product_inline(data['page_office_manager'],
                                                    token=data['token'],
                                                    lang=data['lang'])
        if product:
            await GetAllProductState.get_all.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
            await message.bot.send_message(text=text2, chat_id=message.chat.id,
                                           reply_markup=office_manager_all_product_inline(data['page_office_manager'],
                                                                                          token=data['token'],
                                                                                          lang=data['lang']))
        else:
            text = translate(data['lang'], 'NOT_FOUND_PRODUCT_OFFICE')
            await OrdersState.begin.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=crud_for_office_manager(data['lang']))


@dp.callback_query_handler(state=GetAllProductState.get_all)
async def get_all_product_call_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        props = call.data
        if props.__eq__("exit"):
            text = translate(data['lang'], 'THE_BACK')
            await OrdersState.begin.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=crud_for_office_manager(data['lang']))
            return
        if props.__eq__("prev"):
            data['page'] -= 1
            text = translate(data['lang'], 'THE_ONE_BACK')
            await GetAllProductState.reply_products.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=office_manager_all_product_inline(
                                                    page=data['page_office_manager'], token=data['token'],
                                                    lang=data['lang']))
            return
        if props.__eq__("next"):
            data['page'] += 1
            text = translate(data['lang'], 'THE_ONE_NEXT')
            await GetAllProductState.reply_products.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=office_manager_all_product_inline(
                                                    page=data['page_office_manager'],
                                                    token=data['token'], lang=data['lang']))
            return
        data['product'] = props[1:]
        product_one: dict = get_one_product(product_id=data['product'], token=data['token'])
        product = product_one.get("id")
        name = product_one.get("name")
        composition = product_one.get("composition")
        active = product_one.get("active")
        if active:
            active = translate(data['lang'], "YES_ACTIVE")
        else:
            active = translate(data['lang'], "NO_ACTIVE")
        count = product_one.get("count")
        original_count = product_one.get("original_count")
        size = product_one.get("size")
        expiration_date = product_one.get("expired_date")
        if expiration_date:
            expiration_date = expiration_date[:10]
        image = product_one.get('image')
        price1 = product_one.get("price1")
        price2 = product_one.get("price2")
        seria = product_one.get("seria")
        data['name'] = name
        data['composition'] = composition
        data['active'] = active
        data['count_product'] = count
        data['original_count'] = original_count
        data['size'] = size
        data['expiration_date'] = expiration_date
        data['price1'] = price1
        data['price2'] = price2
        data['seria'] = seria
        data['product_id'] = product
        data['image'] = image
        text = f"{translate(data['lang'], 'NAME')}:\t\t{name}\n{translate(data['lang'], 'CONTENT')}:\t\t{composition}\n{translate(data['lang'], 'COUNT')}:\t\t{price_split(count)}\n{translate(data['lang'], 'ORIGINAL_COUNT')}:\t\t{original_count}\n{translate(data['lang'], 'PRICE50%')}:\t\t{price_split(price1)} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'PRICE100%')}:\t\t{price_split(price2)} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'EXPIRATION_DATE')}:\t\t{expiration_date}\n{translate(data['lang'], 'SERIA')}\t\t{seria}\n{translate(data['lang'], 'STATUS')}:\t\t{active}\n"
        await GetAllProductState.choice.set()
        if not image:
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=choice_office_manager(data['lang']))
        else:
            try:
                await call.message.bot.send_photo(caption=text, photo=data['image'],
                                                  chat_id=call.message.chat.id,
                                                  reply_markup=choice_office_manager(data['lang']))
            except Exception:
                import os
                image_path = os.path.join(PRODUCT_IMAGE, f"{image}.jpg")
                await call.message.bot.send_photo(caption=text, chat_id=call.message.chat.id,
                                                  photo=(open(image_path, 'rb')),
                                                  reply_markup=choice_office_manager(data['lang']))


@dp.callback_query_handler(state=GetAllProductState.choice)
async def choice_product_cal_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data.__eq__('back'):
            text = translate(data['lang'], 'GET_ALL_PRODUCT_TEXT')
            await GetAllProductState.get_all.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=office_manager_all_product_inline(
                                                    data['page_office_manager'],
                                                    token=data['token'], lang=data['lang']))
        if call.data.__eq__('edit'):
            product_one: dict = get_one_product(product_id=data['product'], token=data['token'])
            product = product_one.get("id")
            name = product_one.get("name")
            composition = product_one.get("composition")
            active = product_one.get("active")
            if active:
                active = translate(data['lang'], "YES_ACTIVE")
            else:
                active = translate(data['lang'], "NO_ACTIVE")
            count = product_one.get("count")
            original_count = product_one.get("original_count")
            size = product_one.get("size")
            expiration_date = product_one.get("expired_date")[:10]
            price1 = product_one.get("price1")
            price2 = product_one.get("price2")
            seria = product_one.get("seria")
            data['name'] = name
            data['composition'] = composition
            data['active'] = active
            data['count_product'] = count
            data['original_count'] = original_count
            data['size'] = size
            data['expiration_date'] = expiration_date
            data['price1'] = price1
            data['price2'] = price2
            data['seria'] = seria
            data['image'] = product_one.get('image')
            data['product_id'] = product
            text = f"{translate(data['lang'], 'NAME')}:\t\t{name}\n{translate(data['lang'], 'CONTENT')}:\t\t{composition}\n{translate(data['lang'], 'COUNT')}:\t\t{price_split(count)}\n{translate(data['lang'], 'ORIGINAL_COUNT')}:\n{translate(data['lang'], 'PRICE50%')}:\t\t{price_split(price1)} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'PRICE100%')}:\t\t{price_split(price2)} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'EXPIRATION_DATE')}:\t\t{expiration_date}\n{translate(data['lang'], 'SERIA')}\t\t{seria}\n{translate(data['lang'], 'STATUS')}:\t\t{active}\n\n\t\t\t\t{translate(data['lang'], 'HOW_PARAMETER_UPDATE')}"
            await GetAllProductState.update.set()
            if not data['image']:
                await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                    reply_markup=how_to_edit_for_product(data['lang']))
            else:
                try:
                    await call.message.bot.send_photo(caption=text, photo=data['image'],
                                                      chat_id=call.message.chat.id,
                                                      reply_markup=how_to_edit_for_product(data['lang']))
                except Exception:
                    import os
                    image_path = os.path.join(PRODUCT_IMAGE, f"{data['image']}.jpg")
                    await call.message.bot.send_photo(caption=text, chat_id=call.message.chat.id,
                                                      photo=(open(image_path, 'rb')),
                                                      reply_markup=how_to_edit_for_product(data['lang']))
                # await call.message.bot.send_photo(caption=text, photo=data['image'], chat_id=call.message.chat.id,
                #                                   reply_markup=how_to_edit_for_product(data['lang']))
        if call.data.__eq__('delete'):
            product_one: dict = get_one_product(product_id=data['product'], token=data['token'])
            product = product_one.get("id")
            name = product_one.get("name")
            composition = product_one.get("composition")
            active = product_one.get("active")
            if active:
                active = translate(data['lang'], "YES_ACTIVE")
            else:
                active = translate(data['lang'], "NO_ACTIVE")
            if product_one.get("count"):
                count = product_one.get("count")
            original_count = product_one.get("original_count")
            size = product_one.get("size")
            expiration_date = product_one.get("expired_date")[:10]
            price1 = product_one.get("price1")
            price2 = product_one.get("price2")
            seria = product_one.get("seria")
            data['name'] = name
            data['composition'] = composition
            data['active'] = active
            data['count_product'] = count
            data['original_count'] = original_count
            data['size'] = size
            data['expiration_date'] = expiration_date
            data['price1'] = price1
            data['price2'] = price2
            data['seria'] = seria
            data['image'] = product_one.get('image')
            data['product_id'] = product
            text = f"{translate(data['lang'], 'NAME')}:\t\t{name}\n{translate(data['lang'], 'CONTENT')}:\t\t{composition}\n{translate(data['lang'], 'COUNT')}:\t\t{price_split(count)}\n{translate(data['lang'], 'ORIGINAL_COUNT')}:\n{translate(data['lang'], 'PRICE50%')}:\t\t{price_split(price1)} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'PRICE100%')}:\t\t{price_split(price2)} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'EXPIRATION_DATE')}:\t\t{expiration_date}\n{translate(data['lang'], 'SERIA')}\t\t{seria}\n{translate(data['lang'], 'STATUS')}:\t\t{active}\n\n\t\t\t\t{translate(data['lang'], 'IS_DELETED')}"
            await GetAllProductState.delete.set()
            if data['image']:
                await call.message.bot.send_photo(photo=data['image'], caption=text, chat_id=call.message.chat.id,
                                                  reply_markup=check_basket())
            else:
                try:
                    await call.message.bot.send_photo(caption=text, photo=data['image'],
                                                      chat_id=call.message.chat.id,
                                                      reply_markup=check_basket(data['lang']))
                except Exception:
                    import os
                    image_path = os.path.join(PRODUCT_IMAGE, f"{data['image']}.jpg")
                    await call.message.bot.send_photo(caption=text, chat_id=call.message.chat.id,
                                                      photo=(open(image_path, 'rb')),
                                                      reply_markup=check_basket(data['lang']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[GetAllProductState.choice])
async def create_product_back_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'GET_ALL_PRODUCT_TEXT')
        await GetAllProductState.get_all.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=office_manager_all_product_inline(
                                           data['page_office_manager'],
                                           token=data['token'], lang=data['lang']))
