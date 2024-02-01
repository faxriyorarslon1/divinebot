from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import russian, latin
from api.orders import order_get_one_order, order_update, order_update_params
from api.product import get_one_product, update_product
from api.users.users import get_one_user
from button.inline import all_product_inline, choice_product, \
    check_basket, order_update_all_inline
from button.reply_markup import update_order, base_menu, back_menu, send_update_menu, bron_confirmed_or_unconfirmed_menu
from dispatch import dp
from excel_utils.product_report import PRODUCT_IMAGE
from states import BaseState
from states.bron import UpdateBronState, OrderUpdateState, GetAllBronState
from utils.number_split_for_price import price_split
from utils.props import product_count


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['ORDER_UPDATE_COMMENT_PRODUCTS']) or str(message.text).__eq__(
        russian['ORDER_UPDATE_COMMENT_PRODUCTS']) or str(message.text).__eq__(
        translate_cyrillic_or_latin(latin['ORDER_UPDATE_COMMENT_PRODUCTS'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=UpdateBronState.update)
async def update_message_order_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'HOW_TO_UPDATE_FIELD')
        await OrderUpdateState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=update_order(data['lang']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[OrderUpdateState.begin])
async def back_menu_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['page'] = 1
        text = translate(data['lang'], 'BACK')
        await UpdateBronState.update.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=send_update_menu(data['lang']))


@dp.message_handler(
    lambda message: (message.text.__eq__(russian['UPDATE_COMMENT']) or message.text.__eq__(
        latin['UPDATE_COMMENT']) or message.text.__eq__(
        translate_cyrillic_or_latin(latin['UPDATE_COMMENT'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=OrderUpdateState.begin)
async def update_comment_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'CREATE_COMMENT')
        await OrderUpdateState.update_comment.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id)


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[OrderUpdateState.update_comment, OrderUpdateState.begin])
async def back_menu_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'HOW_TO_UPDATE_FIELD')
        await OrderUpdateState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=update_order(data['lang']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=OrderUpdateState.update_comment)
async def update_new_comment_finished_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        order_one = order_get_one_order(order_id=data['order_id'], token=data['token'])
        data['page'] = 1
        data['products'] = order_one['products']
        data['seller'] = order_one['seller']
        data['comment'] = message.text
        data['inn'] = order_one['inn']
        data['total_price'] = order_one['total_price']
        data['type_price'] = order_one['type_price']
        order_update(products=data['products'],
                     inn=data['inn'],
                     type_price=data['type_price'],
                     token=data['token'],
                     order_id=data['order_id'],
                     seller=data['seller'],
                     is_manager_send=False,
                     comment=data['comment'],
                     total_price=data['total_price'])
        order_one = order_get_one_order(order_id=data['order_id'], token=data['token'])
        text = f"{translate(data['lang'], 'COMPANY_NAME')}:{order_one.get('company_name')}\n{translate(data['lang'], 'INN_GET')}: {order_one.get('inn')}\n{translate(data['lang'], 'COMMENT_GET')}:{order_one.get('comment')}\n\n"
        for i, product in enumerate(order_one.get("products"), start=1):
            product_one = get_one_product(product_id=product.get("product"), token=data['token'])
            text += f"{i}){translate(data['lang'], 'NAME')}:{product_one.get('name')}\n{translate(data['lang'], 'PRICE')}({order_one.get('type_price')}):{price_split(product.get('price'))} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'COUNT')}:{product['count']}"
        text += f"\n{translate(data['lang'], 'CREATED_DATE')}:{str(order_one['created_date'][:10]) + ' ' + order_one['created_date'][11:16]}\n{translate(data['lang'], 'TOTAL_PRICE')}({order_one.get('type_price')}):{price_split(order_one.get('total_price'))} {translate(data['lang'], 'SUM')}"
        text += f"\n{translate(data['lang'], 'SUCCESSFULLY')}"
        await OrderUpdateState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=update_order(data['lang']))


@dp.message_handler(lambda message: (message.text.__eq__(russian['UPDATE_PRODUCT']) or message.text.__eq__(
    latin['UPDATE_PRODUCT']) or message.text.__eq__(translate_cyrillic_or_latin(latin['UPDATE_PRODUCT'], 'cyr'))) and (
                                            not str(message.text).__eq__('/start')),
                    state=OrderUpdateState.begin)
async def update_order_product_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        order_one = order_get_one_order(order_id=data['order_id'], token=data['token'])
        data['page'] = 1
        data['products'] = order_one['products']
        data['seller'] = order_one['seller']
        data['comment'] = order_one['comment']
        data['inn'] = order_one['inn']
        data['total_price'] = order_one['total_price']
        data['type_price'] = order_one['type_price']
        seller = get_one_user(order_one['seller'])
        name = f"{seller['first_name']}"
        if seller['last_name']:
            name = f"{seller['first_name']} {seller['last_name']}"
        text = f"{translate(data['lang'], 'COMPANY_NAME')}:{order_one.get('company_name')}\n{translate(data['lang'], 'INN_GET')}: {order_one.get('inn')}\n{translate(data['lang'], 'COMMENT_GET')}:{order_one.get('comment')}\n{translate(data['lang'], 'CREATOR')}: {translate_cyrillic_or_latin(name, data['lang'])}\n\n"
        for i, product in enumerate(order_one.get("products"), start=1):
            product_one = get_one_product(product.get("product"), token=data['token'])
            text += f"{i}){translate(data['lang'], 'NAME')}:{product_one.get('name')}\n{translate(data['lang'], 'COUNT')}: {product['count']}\n{translate(data['lang'], 'PRICE50%')}:{price_split(product_one.get('price1') * product['count'])} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'PRICE100%')}:{price_split(product_one.get('price2') * product['count'])} {translate(data['lang'], 'SUM')}\n\n"
        text += f"\n{translate(data['lang'], 'CREATED_DATE')}:{str(order_one['created_date'][:10]) + ' ' + order_one['created_date'][11:16]}\n{translate(data['lang'], 'TOTAL_PRICE')}({data['type_price']}): {price_split(data['total_price'])} {translate(data['lang'], 'SUM')}"
        if all_product_inline(page=data['page'], token=data['token']):
            await OrderUpdateState.type_update.set()
            text2 = translate(data['lang'], 'OR_THE_BACK')
            await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
            await message.bot.send_message(text=text2, chat_id=message.chat.id,
                                           reply_markup=all_product_inline(page=data['page'], token=data['token'],
                                                                           lang=data['lang']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[OrderUpdateState.new_product_or_delete])
async def back_menu_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'BACK')
        await OrderUpdateState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=update_order(data['lang']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[OrderUpdateState.new_product_or_delete, OrderUpdateState.type_update])
async def back_menu_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'BACK')
        await OrderUpdateState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=update_order(data['lang']))


@dp.callback_query_handler(state=OrderUpdateState.type_update)
async def cal_for_update_handler(call: types.CallbackQuery, state: FSMContext):
    props = call.data
    async with state.proxy() as data:
        if props.__eq__("exit"):
            text = translate(data['lang'], 'BACK')
            await OrderUpdateState.begin.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=update_order(data['lang']))
            return
        if props.__eq__("prev"):
            data['page'] -= 1
            text = translate(data['lang'], 'THE_ONE_BACK')
            await OrderUpdateState.type_update.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=all_product_inline(page=data['page'], token=data['token'],
                                                                                lang=data['lang']))
            return
        if props.__eq__("next"):
            data['page'] += 1
            text = translate(data['lang'], 'THE_ONE_NEXT')
            await UpdateBronState.type_update.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=all_product_inline(page=data['page'], token=data['token'],
                                                                                lang=data['lang']))
            return
        data['product'] = props[1:]
        product_one: dict = get_one_product(product_id=data['product'], token=data['token'])
        if product_one.get('active'):
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
            image = product_one.get('image')
            data['image'] = image
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
            text = f"{translate(data['lang'], 'NAME')}:\t\t{name}\n{translate(data['lang'], 'CONTENT')}:\t\t{composition}\n{translate(data['lang'], 'ORIGINAL_COUNT')}:\t\t{original_count}\n{translate(data['lang'], 'PRICE50%')}:\t\t{price_split(price1)} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'PRICE100%')}:\t\t{price_split(price2)} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'EXPIRATION_DATE')}:\t\t{expiration_date}\n{translate(data['lang'], 'SERIA')}\t\t{seria}\n{translate(data['lang'], 'STATUS')}:\t\t{active}\n{translate(data['lang'], 'CHOICE_COUNT_UPDATE')}:\t\t\n"
            await OrderUpdateState.count.set()
            if not image:
                await call.message.bot.send_message(text=text, chat_id=call.message.chat.id)
            else:
                try:
                    await call.message.bot.send_photo(caption=text, photo=data['image'], chat_id=call.message.chat.id)
                except Exception:
                    import os
                    image_path = os.path.join(PRODUCT_IMAGE, f"{data['image']}.jpg")
                    await call.message.bot.send_photo(caption=text, chat_id=call.message.chat.id,
                                                      photo=(open(image_path, 'rb')))
            return
        text = translate(data['lang'], 'BACK')
        await OrderUpdateState.begin.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=update_order(data['lang']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=OrderUpdateState.count)
async def create_product_count_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                try:
                    price = int(message.text)
                except Exception:
                    await message.delete()
                    return
                async with state.proxy() as data:
                    in_product = False
                    number = 0
                    old_price = 0
                    price_money = data['price1'] if data['type_price'].__eq__("50%") else data['price2']
                    dict_product = {"product": data["product_id"],
                                    "price": price_money,
                                    "count": price}
                    for i, product in enumerate(data['products']):
                        if product['product'] == dict_product['product']:
                            in_product = True
                            number = i
                    if in_product:
                        if price > data['count_product'] or price < 0:
                            text = translate(data['lang'], 'NOT_FOUND_WAREHOUSE_PRODUCT')
                            await OrderUpdateState.count.set()
                            await message.bot.send_message(text=text, chat_id=message.chat.id)
                            return
                        old_price = data['products'][number]['count']
                        data['products'][number]['count'] = price
                        data['products'][number]['price'] = price_money
                        data['total_price'] -= old_price * price_money
                    else:
                        data['products'].append(dict_product)
                    data['count'] = price
                    data['total_price'] += price_money * price
                    price1 = data['price1']
                    price2 = data['price2']
                    text = f"{translate(data['lang'], 'NAME')}:\t\t{data['name']}\n{translate(data['lang'], 'CONTENT')}:\t\t{data['composition']}\n{translate(data['lang'], 'COUNT')}:\t\t{price_split(data['count'])}\n{translate(data['lang'], 'ORIGINAL_COUNT')}:\t\t{data['original_count']}\n{translate(data['lang'], 'PRICE50%')}:\t\t{price_split(price1)} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'PRICE100%')}:\t\t{price_split(price2)} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'EXPIRATION_DATE')}:\t\t{data['expiration_date']}\n{translate(data['lang'], 'SERIA')}\t\t{data['seria']}\n{translate(data['lang'], 'STATUS')}:\t\t{data['active']}\n"
                    text += f"\n{translate(data['lang'], 'TOTAL_PRICE')}({data['type_price']}):{price_split(data['total_price'])} {translate(data['lang'], 'SUM')}"
                    await OrderUpdateState.check.set()
                    if not data['image']:
                        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                                       reply_markup=choice_product(data['lang']))
                    else:
                        try:
                            await message.bot.send_photo(caption=text, photo=data['image'], chat_id=message.chat.id,
                                                         reply_markup=choice_product(data['lang']))
                        except Exception:
                            import os
                            image_path = os.path.join(PRODUCT_IMAGE, f"{data['image']}.jpg")
                            await message.bot.send_photo(caption=text, chat_id=message.chat.id,
                                                         photo=(open(image_path, 'rb')),
                                                         reply_markup=choice_product(data['lang']))
                        return
                text = translate(data['lang'], 'PRODUCT_NO_ACTIVE')
                await OrderUpdateState.type_update.set()
                await message.bot.send_message(text=text, chat_id=message.chat.id,
                                               reply_markup=all_product_inline(page=data['page'],
                                                                               token=data['token'],
                                                                               lang=data['lang']))
                return
            text = translate(data['lang'], 'BACK')
            await BaseState.base.set()
            user = get_one_user(data['user_id'])
            data['role'] = user['role']
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=base_menu(data['lang'], data['role']))


@dp.callback_query_handler(state=OrderUpdateState.check)
async def check_update_order_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data.__eq__("no"):
            text = translate(data['lang'], 'CHOICE_COUNT')
            await OrderUpdateState.count.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id)
            return
        text = ""
        for i, product in enumerate(data['products'], start=1):
            price1 = price_split(product['price'] * product['count'])
            pr = get_one_product(product['product'], data['token'])
            text += f"{i}\n{translate(data['lang'], 'NAME')}:\t\t{pr['name']}\n{translate(data['lang'], 'COUNT')}:\t\t{product['count']}\n{translate(data['lang'], 'PRICE')}:\t\t{price1} {translate(data['lang'], 'SUM')}\n\n"
        text += f"{translate(data['lang'], 'TOTAL_PRICE')}({data['type_price']}):{price_split(data['total_price'])} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'CHOICE_REPLY')}"
        await OrderUpdateState.choice_product_reply.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=check_basket(data['lang']))


@dp.callback_query_handler(state=OrderUpdateState.choice_product_reply)
async def cal_how_to_order_for_update_or_reply_handler(call: types.CallbackQuery, state: FSMContext):
    props = call.data
    async with state.proxy() as data:
        if props.__eq__("no"):
            data['page'] = 1
            text = translate(data['lang'], 'SUCCESSFULLY')
            for i in data['products']:
                product_one = get_one_product(i['product'], data['token'])
                product = product_one.get("id")
                name = product_one.get('name')
                composition = product_one.get('composition')
                active = product_one.get("active")
                count = product_one.get("count") - i['count']
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
                if count <= 0:
                    active = False
                update_product(name=name, composition=composition, count=count, original_count=original_count,
                               price1=price1,
                               price2=price2, expired_date=expiration_date, seria=seria,
                               active=active,
                               image=image,
                               product_id=product, token=data['token'],
                               created_by=product_one.get('created_by'))
            order_update_params(products=data['products'],
                                inn=data['inn'],
                                type_price=data['type_price'],
                                token=data['token'],
                                order_id=data['order_id'],
                                seller=data['seller'],
                                is_manager_send=False,
                                comment=data['comment'],
                                total_price=data['total_price'])
            await UpdateBronState.update.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=send_update_menu(data['lang']))
        if props.__eq__("yes"):
            text = translate(data['lang'], 'CHOICE_PRODUCT')
            await OrderUpdateState.type_update.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=all_product_inline(
                                                    page=data['page'],
                                                    token=data['token'],
                                                    lang=data['lang'])
                                                )
