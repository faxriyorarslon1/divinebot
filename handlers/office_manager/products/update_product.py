import requests
from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate, translate_cyrillic_or_latin
from Tranlate.translate_language import latin, russian
from api.product import get_one_product, update_product
from api.users.users import get_one_user
from button.inline import office_manager_all_product_inline, how_to_edit_for_product, is_active_inline
from button.reply_markup import base_menu, crud_for_office_manager
from configs.constants import BOT_TOKEN
from dispatch import dp, bot
from excel_utils.product_report import create_product_image, PRODUCT_IMAGE
from states import BaseState
from states.orders import GetAllProductState, OrdersState


@dp.callback_query_handler(state=GetAllProductState.update)
async def edit_for_current_product_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data.__eq__('back'):
            text = translate(data['lang'], 'BACK')
            await GetAllProductState.get_all.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=office_manager_all_product_inline(
                                                    data['page_office_manager'],
                                                    token=data['token'], lang=data['lang']))
        if call.data.__eq__('name'):
            text = translate(data['lang'], 'CREATE_PRODUCT_NAME')
            await GetAllProductState.name.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id)
        if call.data.__eq__('content'):
            text = translate(data['lang'], 'CREATE_PRODUCT_CONTENT')
            await GetAllProductState.content.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id)
        if call.data.__eq__('image'):
            text = translate(data['lang'], 'CREATE_PRODUCT_IMAGE')
            await GetAllProductState.image.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id)
        if call.data.__eq__('price50'):
            text = translate(data['lang'], 'CREATE_PRODUCT_PRICE50%')
            await GetAllProductState.price50.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id)
        if call.data.__eq__('price100'):
            text = translate(data['lang'], 'CREATE_PRODUCT_PRICE100%')
            await GetAllProductState.price100.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id)
        if call.data.__eq__('expiration_date'):
            text = translate(data['lang'], 'CREATE_PRODUCT_EXPIRATION_DATE')
            await GetAllProductState.expiration_date.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id)
        if call.data.__eq__('seria'):
            text = translate(data['lang'], 'CREATE_PRODUCT_SERIA')
            await GetAllProductState.seria.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id)
        if call.data.__eq__('status'):
            text = translate(data['lang'], 'CREATE_PRODUCT_STATUS')
            await GetAllProductState.status.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=is_active_inline(data['lang']))
        if call.data.__eq__('original_count'):
            text = translate(data['lang'], 'CREATE_PRODUCT_ORIGINAL_COUNT')
            await GetAllProductState.original_count.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id)
        if call.data.__eq__('count'):
            text = translate(data['lang'], 'CREATE_PRODUCT_THE_REST')
            await GetAllProductState.count.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id)


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=GetAllProductState.name)
async def update_name_for_product_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                product_one = get_one_product(data['product'], data['token'])
                product = product_one.get("id")
                name = message.text
                composition = product_one.get("composition")
                active = product_one.get("active")
                if active:
                    active = translate(data['lang'], "YES_ACTIVE")
                else:
                    active = translate(data['lang'], "NO_ACTIVE")
                count = product_one.get("count")
                original_count = product_one.get("original_count")
                expiration_date = product_one.get("expired_date")[:10]
                image = product_one.get('image')
                price1 = product_one.get("price1")
                price2 = product_one.get("price2")
                seria = product_one.get("seria")
                data['name'] = name
                data['composition'] = composition
                data['active'] = active
                data['count_product'] = count
                data['original_count'] = original_count
                data['expiration_date'] = expiration_date
                data['price1'] = price1
                data['price2'] = price2
                data['seria'] = seria
                data['image'] = image
                data['product_id'] = product
                update_product(name=name, composition=composition, count=count, original_count=original_count,
                               price1=price1,
                               price2=price2, expired_date=expiration_date, seria=seria,
                               active=product_one.get("active"),
                               image=image,
                               product_id=product, token=data['token'], created_by=product_one.get('created_by'))
                text = f"{translate(data['lang'], 'NAME')}:\t\t{name}\n{translate(data['lang'], 'CONTENT')}:\t\t{composition}\n{translate(data['lang'], 'COUNT')}:\t\t{count}\n{translate(data['lang'], 'ORIGINAL_COUNT')}:\t\t{original_count}\n{translate(data['lang'], 'PRICE50%')}:\t\t{price1}\n{translate(data['lang'], 'PRICE100%')}:\t\t{price2}\n{translate(data['lang'], 'EXPIRATION_DATE')}:\t\t{expiration_date}\n{translate(data['lang'], 'SERIA')}\t\t{seria}\n{translate(data['lang'], 'STATUS')}:\t\t{active}\n\n\t\t\t{translate(data['lang'], 'SUCCESS_UPDATED')}"
                await GetAllProductState.update.set()
                if not image:
                    try:
                        await message.bot.send_photo(caption=text, photo=data['image'], chat_id=message.chat.id,
                                                     reply_markup=how_to_edit_for_product(data['lang']))
                    except Exception:
                        import os
                        image_path = os.path.join(PRODUCT_IMAGE, f"{data['image']}.jpg")
                        await message.bot.send_photo(caption=text, chat_id=message.chat.id,
                                                     photo=(open(image_path, 'rb')),
                                                     reply_markup=how_to_edit_for_product(data['lang']))
                else:
                    await message.bot.send_photo(caption=text, photo=data['image'], chat_id=message.chat.id,
                                                 reply_markup=how_to_edit_for_product(data['lang']))
            else:
                text = translate(data['lang'], 'THE_BACK')
                await GetAllProductState.update.set()
                if not data['image']:
                    await message.bot.send_message(text=text, chat_id=message.chat.id,
                                                   reply_markup=how_to_edit_for_product(data['lang']))
                else:
                    try:
                        await message.bot.send_photo(caption=text, photo=data['image'], chat_id=message.chat.id,
                                                     reply_markup=how_to_edit_for_product(data['lang']))
                    except Exception:
                        import os
                        image_path = os.path.join(PRODUCT_IMAGE, f"{data['image']}.jpg")
                        await message.bot.send_photo(caption=text, chat_id=message.chat.id,
                                                     photo=(open(image_path, 'rb')),
                                                     reply_markup=how_to_edit_for_product(data['lang']))
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=GetAllProductState.content)
async def update_name_for_product_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                product_one = get_one_product(data['product'], data['token'])
                product = product_one.get("id")
                name = product_one.get('name')
                composition = message.text
                active = product_one.get("active")
                if active:
                    active = translate(data['lang'], "YES_ACTIVE")
                else:
                    active = translate(data['lang'], "NO_ACTIVE")
                count = product_one.get("count")
                original_count = product_one.get("original_count")
                expiration_date = product_one.get("expired_date")[:10]
                image = product_one.get('image')
                price1 = product_one.get("price1")
                price2 = product_one.get("price2")
                seria = product_one.get("seria")
                data['name'] = name
                data['composition'] = composition
                data['active'] = active
                data['count_product'] = count
                data['original_count'] = original_count
                data['expiration_date'] = expiration_date
                data['price1'] = price1
                data['price2'] = price2
                data['seria'] = seria
                data['image'] = image
                data['product_id'] = product
                update_product(name=name, composition=composition, count=count, original_count=original_count,
                               price1=price1,
                               price2=price2, expired_date=expiration_date, seria=seria,
                               active=product_one.get("active"),
                               image=image,
                               product_id=product, token=data['token'], created_by=product_one.get('created_by'))
                text = f"{translate(data['lang'], 'NAME')}:\t\t{name}\n{translate(data['lang'], 'CONTENT')}:\t\t{composition}\n{translate(data['lang'], 'COUNT')}:\t\t{count}\n{translate(data['lang'], 'ORIGINAL_COUNT')}:\t\t{original_count}\n{translate(data['lang'], 'PRICE50%')}:\t\t{price1}\n{translate(data['lang'], 'PRICE100%')}:\t\t{price2}\n{translate(data['lang'], 'EXPIRATION_DATE')}:\t\t{expiration_date}\n{translate(data['lang'], 'SERIA')}\t\t{seria}\n{translate(data['lang'], 'STATUS')}:\t\t{active}\n\n\t\t\t{translate(data['lang'], 'SUCCESS_UPDATED')}"
                await GetAllProductState.update.set()
                if not image:
                    await message.bot.send_message(text=text, chat_id=message.chat.id,
                                                   reply_markup=how_to_edit_for_product(data['lang']))
                else:
                    try:
                        await message.bot.send_photo(caption=text, photo=data['image'], chat_id=message.chat.id,
                                                     reply_markup=how_to_edit_for_product(data['lang']))
                    except Exception:
                        import os
                        image_path = os.path.join(PRODUCT_IMAGE, f"{data['image']}.jpg")
                        await message.bot.send_photo(caption=text, chat_id=message.chat.id,
                                                     photo=(open(image_path, 'rb')),
                                                     reply_markup=how_to_edit_for_product(data['lang']))
            else:
                text = translate(data['lang'], 'THE_BACK')
                await GetAllProductState.update.set()
                if not data['image']:
                    await message.bot.send_message(text=text, chat_id=message.chat.id,
                                                   reply_markup=how_to_edit_for_product(data['lang']))
                else:
                    await GetAllProductState.update.set()
                    try:
                        await message.bot.send_photo(caption=text, photo=data['image'], chat_id=message.chat.id,
                                                     reply_markup=how_to_edit_for_product(data['lang']))
                    except Exception:
                        import os
                        image_path = os.path.join(PRODUCT_IMAGE, f"{data['image']}.jpg")
                        await message.bot.send_photo(caption=text, chat_id=message.chat.id,
                                                     photo=(open(image_path, 'rb')),
                                                     reply_markup=how_to_edit_for_product(data['lang']))
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=GetAllProductState.price50)
async def update_name_for_product_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                try:
                    int(message.text)
                except Exception:
                    await message.delete()
                    return
                product_one = get_one_product(data['product'], data['token'])
                product = product_one.get("id")
                name = product_one.get('name')
                composition = product_one.get('composition')
                active = product_one.get("active")
                if active:
                    active = translate(data['lang'], "YES_ACTIVE")
                else:
                    active = translate(data['lang'], "NO_ACTIVE")
                count = product_one.get("count")
                original_count = product_one.get("original_count")
                expiration_date = product_one.get("expired_date")[:10]
                image = product_one.get('image')
                price1 = int(message.text)
                price2 = product_one.get("price2")
                seria = product_one.get("seria")
                data['name'] = name
                data['composition'] = composition
                data['active'] = active
                data['count_product'] = count
                data['original_count'] = original_count
                # data['size'] = size
                data['expiration_date'] = expiration_date
                data['price1'] = price1
                data['price2'] = price2
                data['seria'] = seria
                data['image'] = image
                data['product_id'] = product
                update_product(name=name, composition=composition, count=count, original_count=original_count,
                               price1=price1,
                               price2=price2, expired_date=expiration_date, seria=seria,
                               active=product_one.get("active"),
                               image=image,
                               product_id=product, token=data['token'], created_by=product_one.get('created_by'))
                text = f"{translate(data['lang'], 'NAME')}:\t\t{name}\n{translate(data['lang'], 'CONTENT')}:\t\t{composition}\n{translate(data['lang'], 'COUNT')}:\t\t{count}\n{translate(data['lang'], 'ORIGINAL_COUNT')}:\t\t{original_count}\n{translate(data['lang'], 'PRICE50%')}:\t\t{price1}\n{translate(data['lang'], 'PRICE100%')}:\t\t{price2}\n{translate(data['lang'], 'EXPIRATION_DATE')}:\t\t{expiration_date}\n{translate(data['lang'], 'SERIA')}\t\t{seria}\n{translate(data['lang'], 'STATUS')}:\t\t{active}\n\n\t\t\t{translate(data['lang'], 'SUCCESS_UPDATED')}"
                await GetAllProductState.update.set()
                if not image:
                    await message.bot.send_message(text=text, chat_id=message.chat.id,
                                                   reply_markup=how_to_edit_for_product(data['lang']))
                else:
                    await message.bot.send_photo(caption=text, photo=data['image'], chat_id=message.chat.id,
                                                 reply_markup=how_to_edit_for_product(data['lang']))
            else:
                text = translate(data['lang'], 'THE_BACK')
                await GetAllProductState.update.set()
                if not data['image']:
                    await message.bot.send_message(text=text, chat_id=message.chat.id,
                                                   reply_markup=how_to_edit_for_product(data['lang']))
                else:
                    try:
                        await message.bot.send_photo(caption=text, photo=data['image'], chat_id=message.chat.id,
                                                     reply_markup=how_to_edit_for_product(data['lang']))
                    except Exception:
                        import os
                        image_path = os.path.join(PRODUCT_IMAGE, f"{data['image']}.jpg")
                        await message.bot.send_photo(caption=text, chat_id=message.chat.id,
                                                     photo=(open(image_path, 'rb')),
                                                     reply_markup=how_to_edit_for_product(data['lang']))
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.callback_query_handler(state=GetAllProductState.status)
async def update_name_for_product_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if not (call.message.text.__eq__(latin['BACK_MENU']) or call.message.text.__eq__(
                russian['BACK_MENU']) or call.message.text.__eq__(
            translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
            product_one = get_one_product(data['product'], data['token'])
            product = product_one.get("id")
            name = product_one.get('name')
            composition = product_one.get('composition')
            active = product_one.get("active")
            if call.data.__eq__('active'):
                active = translate(data['lang'], "YES_ACTIVE")
            else:
                active = translate(data['lang'], "NO_ACTIVE")
            count = product_one.get("count")
            original_count = product_one.get("original_count")
            expiration_date = product_one.get("expired_date")[:10]
            image = product_one.get('image')
            price1 = product_one.get('price1')
            price2 = product_one.get("price2")
            seria = product_one.get("seria")
            data['name'] = name
            data['composition'] = composition
            data['active'] = active
            data['count_product'] = count
            data['original_count'] = original_count
            # data['size'] = size
            data['expiration_date'] = expiration_date
            data['price1'] = price1
            data['price2'] = price2
            data['seria'] = seria
            data['image'] = image
            data['product_id'] = product
            actives = None
            if call.data.__eq__('no_active'):
                actives = False
            else:
                actives = True
            update_product(name=name, composition=composition, count=count, original_count=original_count,
                           price1=price1,
                           price2=price2, expired_date=expiration_date, seria=seria, active=actives,
                           image=image,
                           product_id=product, token=data['token'], created_by=product_one.get('created_by'))
            text = f"{translate(data['lang'], 'NAME')}:\t\t{name}\n{translate(data['lang'], 'CONTENT')}:\t\t{composition}\n{translate(data['lang'], 'COUNT')}:\t\t{count}\n{translate(data['lang'], 'ORIGINAL_COUNT')}:\t\t{original_count}\n{translate(data['lang'], 'PRICE50%')}:\t\t{price1}\n{translate(data['lang'], 'PRICE100%')}:\t\t{price2}\n{translate(data['lang'], 'EXPIRATION_DATE')}:\t\t{expiration_date}\n{translate(data['lang'], 'SERIA')}\t\t{seria}\n{translate(data['lang'], 'STATUS')}:\t\t{active}\n\n\t\t\t{translate(data['lang'], 'SUCCESS_UPDATED')}"
            await GetAllProductState.update.set()
            if not image:
                await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                    reply_markup=how_to_edit_for_product(data['lang']))
            else:
                try:
                    await call.message.bot.send_photo(caption=text, photo=data['image'], chat_id=call.message.chat.id,
                                                      reply_markup=how_to_edit_for_product(data['lang']))
                except Exception:
                    import os
                    image_path = os.path.join(PRODUCT_IMAGE, f"{data['image']}.jpg")
                    await call.message.bot.send_photo(caption=text, chat_id=call.message.chat.id,
                                                      photo=(open(image_path, 'rb')),
                                                      reply_markup=how_to_edit_for_product(data['lang']))
        else:
            text = translate(data['lang'], 'THE_BACK')
            await GetAllProductState.update.set()
            if not data['image']:
                await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                    reply_markup=how_to_edit_for_product(data['lang']))
            else:
                await call.message.bot.send_photo(caption=text, photo=data['image'], chat_id=call.message.chat.id,
                                                  reply_markup=how_to_edit_for_product(data['lang']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[GetAllProductState.status])
async def create_product_back_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'THE_BACK')
        await GetAllProductState.update.set()
        if not data['image']:
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=how_to_edit_for_product(data['lang']))
        else:
            try:
                await message.bot.send_photo(caption=text, photo=data['image'], chat_id=message.chat.id,
                                             reply_markup=how_to_edit_for_product(data['lang']))
            except Exception:
                import os
                image_path = os.path.join(PRODUCT_IMAGE, f"{data['image']}.jpg")
                await message.bot.send_photo(caption=text, chat_id=message.chat.id, photo=(open(image_path, 'rb')),
                                             reply_markup=how_to_edit_for_product(data['lang']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=GetAllProductState.price100)
async def update_name_for_product_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                try:
                    int(message.text)
                except Exception:
                    await message.delete()
                    return
                product_one = get_one_product(data['product'], data['token'])
                product = product_one.get("id")
                name = product_one.get('name')
                composition = product_one.get('composition')
                active = product_one.get("active")
                if active:
                    active = translate(data['lang'], "YES_ACTIVE")
                else:
                    active = translate(data['lang'], "NO_ACTIVE")
                count = product_one.get("count")
                original_count = product_one.get("original_count")
                expiration_date = product_one.get("expired_date")[:10]
                image = product_one.get('image')
                price2 = int(message.text)
                price1 = product_one.get("price1")
                seria = product_one.get("seria")
                data['name'] = name
                data['composition'] = composition
                data['active'] = active
                data['count_product'] = count
                data['original_count'] = original_count
                # data['size'] = size
                data['expiration_date'] = expiration_date
                data['price1'] = price1
                data['price2'] = price2
                data['seria'] = seria
                data['image'] = image
                data['product_id'] = product
                update_product(name=name, composition=composition, count=count, original_count=original_count,
                               price1=price1,
                               price2=price2, expired_date=expiration_date, seria=seria,
                               active=product_one.get("active"),
                               image=image,
                               product_id=product, token=data['token'], created_by=product_one.get('created_by'))
                text = f"{translate(data['lang'], 'NAME')}:\t\t{name}\n{translate(data['lang'], 'CONTENT')}:\t\t{composition}\n{translate(data['lang'], 'COUNT')}:\t\t{count}\n{translate(data['lang'], 'ORIGINAL_COUNT')}:\t\t{original_count}\n{translate(data['lang'], 'PRICE50%')}:\t\t{price1}\n{translate(data['lang'], 'PRICE100%')}:\t\t{price2}\n{translate(data['lang'], 'EXPIRATION_DATE')}:\t\t{expiration_date}\n{translate(data['lang'], 'SERIA')}\t\t{seria}\n{translate(data['lang'], 'STATUS')}:\t\t{active}\n\n\t\t\t{translate(data['lang'], 'SUCCESS_UPDATED')}"
                await GetAllProductState.update.set()
                if not image:
                    await message.bot.send_message(text=text, chat_id=message.chat.id,
                                                   reply_markup=how_to_edit_for_product(data['lang']))
                else:
                    await message.bot.send_photo(caption=text, photo=data['image'], chat_id=message.chat.id,
                                                 reply_markup=how_to_edit_for_product(data['lang']))
            else:
                text = translate(data['lang'], 'THE_BACK')
                await GetAllProductState.update.set()
                if not data['image']:
                    await message.bot.send_message(text=text, chat_id=message.chat.id,
                                                   reply_markup=how_to_edit_for_product(data['lang']))
                else:
                    try:
                        await message.bot.send_photo(caption=text, photo=data['image'], chat_id=message.chat.id,
                                                     reply_markup=how_to_edit_for_product(data['lang']))
                    except Exception:
                        import os
                        image_path = os.path.join(PRODUCT_IMAGE, f"{data['image']}.jpg")
                        await message.bot.send_photo(caption=text, chat_id=message.chat.id,
                                                     photo=(open(image_path, 'rb')),
                                                     reply_markup=how_to_edit_for_product(data['lang']))
                return
            text = translate(data['lang'], 'BACK')
            await BaseState.base.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=GetAllProductState.expiration_date)
async def update_name_for_product_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                try:
                    int(message.text[:4]) and int(message.text[5:7]) and int(message.text[8:])
                except Exception:
                    await message.delete()
                    return
                product_one = get_one_product(data['product'], data['token'])
                product = product_one.get("id")
                name = product_one.get('name')
                composition = product_one.get('composition')
                active = product_one.get("active")
                if active:
                    active = translate(data['lang'], "YES_ACTIVE")
                else:
                    active = translate(data['lang'], "NO_ACTIVE")
                count = product_one.get("count")
                original_count = product_one.get('original_count')
                expiration_date = message.text
                image = product_one.get('image')
                price2 = product_one.get('price2')
                price1 = product_one.get("price1")
                seria = product_one.get("seria")
                data['name'] = name
                data['composition'] = composition
                data['active'] = active
                data['count_product'] = count
                data['original_count'] = original_count
                data['expiration_date'] = expiration_date
                data['price1'] = price1
                data['price2'] = price2
                data['seria'] = seria
                data['image'] = image
                data['product_id'] = product
                update_product(name=name, composition=composition, count=count, original_count=original_count,
                               price1=price1,
                               price2=price2, expired_date=expiration_date, seria=seria,
                               active=product_one.get("active"),
                               image=image,
                               product_id=product, token=data['token'], created_by=product_one.get('created_by'))
                text = f"{translate(data['lang'], 'NAME')}:\t\t{name}\n{translate(data['lang'], 'CONTENT')}:\t\t{composition}\n{translate(data['lang'], 'COUNT')}:\t\t{count}\n{translate(data['lang'], 'ORIGINAL_COUNT')}:\t\t{original_count}\n{translate(data['lang'], 'PRICE50%')}:\t\t{price1}\n{translate(data['lang'], 'PRICE100%')}:\t\t{price2}\n{translate(data['lang'], 'EXPIRATION_DATE')}:\t\t{expiration_date}\n{translate(data['lang'], 'SERIA')}\t\t{seria}\n{translate(data['lang'], 'STATUS')}:\t\t{active}\n\n\t\t\t{translate(data['lang'], 'SUCCESS_UPDATED')}"
                await GetAllProductState.update.set()
                if not image:
                    await message.bot.send_message(text=text, chat_id=message.chat.id,
                                                   reply_markup=how_to_edit_for_product(data['lang']))
                else:
                    await message.bot.send_photo(caption=text, photo=data['image'], chat_id=message.chat.id,
                                                 reply_markup=how_to_edit_for_product(data['lang']))
            else:
                text = translate(data['lang'], 'THE_BACK')
                await GetAllProductState.update.set()
                if not data['image']:
                    await message.bot.send_message(text=text, chat_id=message.chat.id,
                                                   reply_markup=how_to_edit_for_product(data['lang']))
                else:
                    try:
                        await message.bot.send_photo(caption=text, photo=data['image'], chat_id=message.chat.id,
                                                     reply_markup=how_to_edit_for_product(data['lang']))
                    except Exception:
                        import os
                        image_path = os.path.join(PRODUCT_IMAGE, f"{data['image']}.jpg")
                        await message.bot.send_photo(caption=text, chat_id=message.chat.id,
                                                     photo=(open(image_path, 'rb')),
                                                     reply_markup=how_to_edit_for_product(data['lang']))
                return
            text = translate(data['lang'], 'BACK')
            await BaseState.base.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=GetAllProductState.seria)
async def update_name_for_product_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                product_one = get_one_product(data['product'], data['token'])
                product = product_one.get("id")
                name = product_one.get('name')
                composition = product_one.get('composition')
                active = product_one.get("active")
                if active:
                    active = translate(data['lang'], "YES_ACTIVE")
                else:
                    active = translate(data['lang'], "NO_ACTIVE")
                count = product_one.get('count')
                original_count = product_one.get("original_count")
                expiration_date = product_one.get("expired_date")[:10]
                image = product_one.get('image')
                price2 = product_one.get('price2')
                price1 = product_one.get("price1")
                seria = message.text
                data['name'] = name
                data['composition'] = composition
                data['active'] = active
                data['count_product'] = count
                data['original_count'] = original_count
                data['expiration_date'] = expiration_date
                data['price1'] = price1
                data['price2'] = price2
                data['seria'] = seria
                data['image'] = image
                data['product_id'] = product
                update_product(name=name, composition=composition, count=count, original_count=original_count,
                               price1=price1,
                               price2=price2, expired_date=expiration_date, seria=seria,
                               active=product_one.get("active"),
                               image=image,
                               product_id=product, token=data['token'], created_by=product_one.get('created_by'))
                text = f"{translate(data['lang'], 'NAME')}:\t\t{name}\n{translate(data['lang'], 'CONTENT')}:\t\t{composition}\n{translate(data['lang'], 'COUNT')}:\t\t{count}\n{translate(data['lang'], 'ORIGINAL_COUNT')}:\t\t{original_count}\n{translate(data['lang'], 'PRICE50%')}:\t\t{price1}\n{translate(data['lang'], 'PRICE100%')}:\t\t{price2}\n{translate(data['lang'], 'EXPIRATION_DATE')}:\t\t{expiration_date}\n{translate(data['lang'], 'SERIA')}\t\t{seria}\n{translate(data['lang'], 'STATUS')}:\t\t{active}\n\n\t\t\t{translate(data['lang'], 'SUCCESS_UPDATED')}"
                await GetAllProductState.update.set()
                if not image:
                    await message.bot.send_message(text=text, chat_id=message.chat.id,
                                                   reply_markup=how_to_edit_for_product(data['lang']))
                else:
                    await message.bot.send_photo(caption=text, photo=data['image'], chat_id=message.chat.id,
                                                 reply_markup=how_to_edit_for_product(data['lang']))
            else:
                text = translate(data['lang'], 'THE_BACK')
                await GetAllProductState.update.set()
                if not data['image']:
                    await message.bot.send_message(text=text, chat_id=message.chat.id,
                                                   reply_markup=how_to_edit_for_product(data['lang']))
                else:
                    try:
                        await message.bot.send_photo(caption=text, photo=data['image'], chat_id=message.chat.id,
                                                     reply_markup=how_to_edit_for_product(data['lang']))
                    except Exception:
                        import os
                        image_path = os.path.join(PRODUCT_IMAGE, f"{data['image']}.jpg")
                        await message.bot.send_photo(caption=text, chat_id=message.chat.id,
                                                     photo=(open(image_path, 'rb')),
                                                     reply_markup=how_to_edit_for_product(data['lang']))
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=GetAllProductState.count)
async def update_name_for_product_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                product_one = get_one_product(data['product'], data['token'])
                product = product_one.get("id")
                name = product_one.get('name')
                composition = product_one.get('composition')
                active = product_one.get("active")
                if active:
                    active = translate(data['lang'], "YES_ACTIVE")
                else:
                    active = translate(data['lang'], "NO_ACTIVE")
                count = message.text
                original_count = product_one.get("original_count")
                expiration_date = product_one.get("expired_date")[:10]
                image = product_one.get('image')
                price2 = product_one.get('price2')
                price1 = product_one.get("price1")
                seria = product_one.get('seria')
                data['name'] = name
                data['composition'] = composition
                data['active'] = active
                data['count_product'] = count
                data['original_count'] = original_count
                data['expiration_date'] = expiration_date
                data['price1'] = price1
                data['price2'] = price2
                data['seria'] = seria
                data['image'] = image
                data['product_id'] = product
                update_product(name=name, composition=composition, count=count, original_count=original_count,
                               price1=price1,
                               price2=price2, expired_date=expiration_date, seria=seria,
                               active=product_one.get("active"),
                               image=image,
                               product_id=product, token=data['token'], created_by=product_one.get('created_by'))
                text = f"{translate(data['lang'], 'NAME')}:\t\t{name}\n{translate(data['lang'], 'CONTENT')}:\t\t{composition}\n{translate(data['lang'], 'COUNT')}:\t\t{count}\n{translate(data['lang'], 'ORIGINAL_COUNT')}:\t\t{original_count}\n{translate(data['lang'], 'PRICE50%')}:\t\t{price1}\n{translate(data['lang'], 'PRICE100%')}:\t\t{price2}\n{translate(data['lang'], 'EXPIRATION_DATE')}:\t\t{expiration_date}\n{translate(data['lang'], 'SERIA')}\t\t{seria}\n{translate(data['lang'], 'STATUS')}:\t\t{active}\n\n\t\t\t{translate(data['lang'], 'SUCCESS_UPDATED')}"
                await GetAllProductState.update.set()
                if not image:
                    await message.bot.send_message(text=text, chat_id=message.chat.id,
                                                   reply_markup=how_to_edit_for_product(data['lang']))
                else:
                    await message.bot.send_photo(caption=text, photo=data['image'], chat_id=message.chat.id,
                                                 reply_markup=how_to_edit_for_product(data['lang']))
            else:
                text = translate(data['lang'], 'THE_BACK')
                await GetAllProductState.update.set()
                if not data['image']:
                    await message.bot.send_message(text=text, chat_id=message.chat.id,
                                                   reply_markup=how_to_edit_for_product(data['lang']))
                else:
                    try:
                        await message.bot.send_photo(caption=text, photo=data['image'], chat_id=message.chat.id,
                                                     reply_markup=how_to_edit_for_product(data['lang']))
                    except Exception:
                        import os
                        image_path = os.path.join(PRODUCT_IMAGE, f"{data['image']}.jpg")
                        await message.bot.send_photo(caption=text, chat_id=message.chat.id,
                                                     photo=(open(image_path, 'rb')),
                                                     reply_markup=how_to_edit_for_product(data['lang']))
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=GetAllProductState.original_count)
async def update_name_for_product_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                product_one = get_one_product(data['product'], data['token'])
                product = product_one.get("id")
                name = product_one.get('name')
                composition = product_one.get('composition')
                active = product_one.get("active")
                if active:
                    active = translate(data['lang'], "YES_ACTIVE")
                else:
                    active = translate(data['lang'], "NO_ACTIVE")
                count = product_one.get("count")
                original_count = int(message.text)
                expiration_date = product_one.get("expired_date")[:10]
                image = product_one.get('image')
                price2 = product_one.get('price2')
                price1 = product_one.get("price1")
                seria = product_one.get("seria")
                data['name'] = name
                data['composition'] = composition
                data['active'] = active
                data['count_product'] = count
                data['original_count'] = original_count
                data['expiration_date'] = expiration_date
                data['price1'] = price1
                data['price2'] = price2
                data['seria'] = seria
                data['image'] = image
                data['product_id'] = product
                update_product(name=name, composition=composition, count=count, original_count=original_count,
                               price1=price1,
                               price2=price2, expired_date=expiration_date, seria=seria,
                               active=product_one.get("active"),
                               image=image,
                               product_id=product, token=data['token'], created_by=product_one.get('created_by'))
                text = f"{translate(data['lang'], 'NAME')}:\t\t{name}\n{translate(data['lang'], 'CONTENT')}:\t\t{composition}\n{translate(data['lang'], 'COUNT')}:\t\t{count}\n{translate(data['lang'], 'ORIGINAL_COUNT')}:\t\t{original_count}\n{translate(data['lang'], 'PRICE50%')}:\t\t{price1}\n{translate(data['lang'], 'PRICE100%')}:\t\t{price2}\n{translate(data['lang'], 'EXPIRATION_DATE')}:\t\t{expiration_date}\n{translate(data['lang'], 'SERIA')}\t\t{seria}\n{translate(data['lang'], 'STATUS')}:\t\t{active}\n\n\t\t\t{translate(data['lang'], 'SUCCESS_UPDATED')}"
                await GetAllProductState.update.set()
                if not image:
                    await message.bot.send_message(text=text, chat_id=message.chat.id,
                                                   reply_markup=how_to_edit_for_product(data['lang']))
                else:
                    await message.bot.send_photo(caption=text, photo=data['image'], chat_id=message.chat.id,
                                                 reply_markup=how_to_edit_for_product(data['lang']))
            else:
                text = translate(data['lang'], 'THE_BACK')
                await GetAllProductState.update.set()
                if not data['image']:
                    await message.bot.send_message(text=text, chat_id=message.chat.id,
                                                   reply_markup=how_to_edit_for_product(data['lang']))
                else:
                    try:
                        await message.bot.send_photo(caption=text, photo=data['image'], chat_id=message.chat.id,
                                                     reply_markup=how_to_edit_for_product(data['lang']))
                    except Exception:
                        import os
                        image_path = os.path.join(PRODUCT_IMAGE, f"{data['image']}.jpg")
                        await message.bot.send_photo(caption=text, chat_id=message.chat.id,
                                                     photo=(open(image_path, 'rb')),
                                                     reply_markup=how_to_edit_for_product(data['lang']))
                return
            text = translate(data['lang'], 'BACK')
            await BaseState.base.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), content_types=types.ContentType.PHOTO,
                    state=GetAllProductState.image)
async def update_name_for_product_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        product_one = get_one_product(data['product'], data['token'])
        product = product_one.get("id")
        name = product_one.get('name')
        composition = product_one.get('composition')
        active = product_one.get("active")
        if active:
            active = translate(data['lang'], "YES_ACTIVE")
        else:
            active = translate(data['lang'], "NO_ACTIVE")
        count = product_one.get("count")
        original_count = product_one.get("original_count")
        expiration_date = product_one.get("expired_date")[:10]
        image = message.photo[-1].file_id
        price1 = product_one.get("price1")
        price2 = product_one.get("price2")
        seria = product_one.get("seria")
        data['name'] = name
        data['composition'] = composition
        data['active'] = active
        data['count_product'] = count
        data['original_count'] = original_count
        # data['size'] = size
        data['expiration_date'] = expiration_date
        data['price1'] = price1
        data['price2'] = price2
        data['seria'] = seria
        data['image'] = image
        data['product_id'] = product
        update_product(name=name, composition=composition, count=count, original_count=original_count,
                       price1=price1,
                       price2=price2, expired_date=expiration_date, seria=seria, active=product_one.get("active"),
                       image=image,
                       product_id=product, token=data['token'], created_by=product_one.get('created_by'))
        file = await bot.get_file(image)
        file_pah = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"
        response = requests.get(file_pah)
        create_product_image(image, response.content, file_pah)
        text = translate(data['lang'], 'THE_BACK')
        await GetAllProductState.update.set()
        if not data['image']:
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=how_to_edit_for_product(data['lang']))
        else:
            try:
                await message.bot.send_photo(caption=text, photo=data['image'], chat_id=message.chat.id,
                                             reply_markup=how_to_edit_for_product(data['lang']))
            except Exception:
                import os
                image_path = os.path.join(PRODUCT_IMAGE, f"{data['image']}.jpg")
                await message.bot.send_photo(caption=text, chat_id=message.chat.id, photo=(open(image_path, 'rb')),
                                             reply_markup=how_to_edit_for_product(data['lang']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), content_types=types.ContentType.ANY,
                    state=GetAllProductState.image)
async def any_message_handler(message: types.Message):
    await message.delete()
    return
