from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import latin, russian
from api.orders import order_create
from api.orders.company import Company
from api.product import get_one_product, update_product
from api.users import district_retrieve
from api.users.users import get_one_user, get_chat_id, get_office_managers
from button.inline import all_product_inline, choice_product, choice_price_markup, check_agreement, check_basket, \
    create_inn_choice, company_all_inline, create_count
from button.reply_markup import bron_menu, back_menu, base_menu
from dispatch import dp
from excel_utils.product_report import PRODUCT_IMAGE
from states import BaseState
from states.bron import BronState, CreateBronState, CreateCompanyState
from utils.number_split_for_price import price_split


@dp.message_handler(lambda message: (str(message.text).__eq__(latin['CREATE_ORDER']) or str(message.text).__eq__(
    russian['CREATE_ORDER']) or str(message.text).__eq__(
    translate_cyrillic_or_latin(latin['CREATE_ORDER'], 'cyr'))) and (
                                            not str(message.text).__eq__('/start')),
                    state=BronState.bron)
async def create_bron_begin_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['page'] = 1
        data['search'] = None
        text = translate(data['lang'], 'CHOICE_COMPANY')
        text2 = translate(data['lang'], 'OR_SEARCH')
        await BronState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
        await message.bot.send_message(text=text2, chat_id=message.chat.id,
                                       reply_markup=company_all_inline(data['page'], data['search'], data['token'],
                                                                       data['lang']))


@dp.callback_query_handler(state=BronState.begin)
async def cal_company_state_message_handler(call: types.CallbackQuery, state: FSMContext):
    props = call.data
    async with state.proxy() as data:
        if props.__eq__("prev"):
            data['page'] -= 1
            text = translate(data['lang'], 'THE_ONE_BACK')
            await BronState.begin.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=company_all_inline(data['page'], data['search'],
                                                                                data['token'],
                                                                                data['lang']))
            return
        if props.__eq__("next"):
            data['page'] += 1
            text = translate(data['lang'], 'THE_ONE_NEXT')
            await BronState.begin.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=company_all_inline(data['page'], data['search'],
                                                                                data['token'],
                                                                                data['lang']))
            return
        if props.__eq__('new'):
            text = translate(data['lang'], 'CREATE_COMPANY_INN')
            await CreateCompanyState.inn.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id)
            return
        if props.__eq__("back"):
            text = translate(data['lang'], 'BACK')
            await BronState.bron.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=bron_menu(data['lang']))
            return
        data['company_id'] = props[1:]
        company = Company(company_id=props[1:], token=data['token']).get_one()
        if company.get('company_name'):
            data['companyName'] = company['company_name']
        if company.get('phone_number'):
            data["companyPhone"] = company['phone_number']
        if company.get('company_address'):
            data['companyAddress'] = company['company_address']
        if company.get('bank_name'):
            data['companyBank'] = company['bank_name']
        if company.get('inn'):
            data['order_inn'] = company['inn']
        data['page'] = 1
        data['all_price1'] = 0
        data['all_price2'] = 0
        data['products'] = list()
        data['products_dict'] = list()
        text = translate(data['lang'], 'CHOICE_PRODUCT')
        text2 = translate(data['lang'], 'OR_THE_BACK')
        if all_product_inline(page=data['page'], token=data['token']):
            await CreateBronState.products.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=back_menu(data['lang']))
            await call.message.bot.send_message(text=text2, chat_id=call.message.chat.id,
                                                reply_markup=all_product_inline(page=data['page'], token=data['token'],
                                                                                lang=data['lang']))
            return
        text = translate(data['lang'], "NOT_FOUND_PRODUCT")
        await BronState.bron.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=bron_menu(data['lang']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=BronState.begin)
async def search_for_company_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                data['page'] = 1
                data['search'] = message.text
                text = translate(data['lang'], 'CHOICE_COMPANY')
                text2 = translate(data['lang'], 'OR_SEARCH')
                await BronState.begin.set()
                await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
                await message.bot.send_message(text=text2, chat_id=message.chat.id,
                                               reply_markup=company_all_inline(data['page'], data['search'],
                                                                               data['token'],
                                                                               data['lang']))
                return
            text = translate(data['lang'], 'BACK')
            await BronState.bron.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=bron_menu(data['lang']))
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.callback_query_handler(state=BronState.begin)
async def cal_company_state_message_handler(call: types.CallbackQuery, state: FSMContext):
    props = call.data
    async with state.proxy() as data:
        if props.__eq__("prev"):
            data['page'] -= 1
            text = translate(data['lang'], 'THE_ONE_BACK')
            await BronState.begin.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=company_all_inline(data['page'], data['search'],
                                                                                data['token'],
                                                                                data['lang']))
            return
        if props.__eq__("next"):
            data['page'] += 1
            text = translate(data['lang'], 'THE_ONE_NEXT')
            await BronState.begin.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=company_all_inline(data['page'], data['search'],
                                                                                data['token'],
                                                                                data['lang']))
            return
        if props.__eq__('new'):
            text = translate(data['lang'], 'CREATE_COMPANY_INN')
            await CreateCompanyState.inn.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id)
            return
        if props.__eq__("back"):
            text = translate(data['lang'], 'THE_ONE_NEXT')
            await BronState.begin.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=company_all_inline(data['page'], data['search'],
                                                                                data['token'],
                                                                                data['lang']))
            return
        data['company_id'] = props[1:]
        company = Company(company_id=props[1:], token=data['token']).get_one()
        data['companyName'] = company['company_name']
        data["companyPhone"] = company['phone_number']
        data['companyAddress'] = company['company_address']
        data['companyBank'] = company['bank_name']
        data['order_inn'] = company['inn']
        data['page'] = 1
        data['all_price1'] = 0
        data['all_price2'] = 0
        data['products'] = list()
        data['products_dict'] = list()
        text = translate(data['lang'], 'CHOICE_PRODUCT')
        text2 = translate(data['lang'], 'OR_THE_BACK')
        if all_product_inline(page=data['page'], token=data['token']):
            await CreateBronState.products.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=back_menu(data['lang']))
            await call.message.bot.send_message(text=text2, chat_id=call.message.chat.id,
                                                reply_markup=all_product_inline(page=data['page'], token=data['token'],
                                                                                lang=data['lang']))
            return
        text = translate(data['lang'], "NOT_FOUND")
        await BronState.begin.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=company_all_inline(data['search'],
                                                                            data['token'],
                                                                            data['lang']))


@dp.message_handler(lambda message: (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
    russian['BACK_MENU']) or message.text.__eq__(
    translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                                            not str(message.text).__eq__('/start')), state=CreateBronState.products)
async def create_product_back_menu_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], "NOT_FOUND")
        await BronState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=company_all_inline(data['search'],
                                                                       data['token'],
                                                                       data['lang']))


@dp.callback_query_handler(state=CreateBronState.products)
async def product_create_handler(call: types.CallbackQuery, state: FSMContext):
    props = call.data
    async with state.proxy() as data:
        if props.__eq__("exit"):
            text = translate(data['lang'], "THE_BACK")
            await BronState.bron.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=bron_menu(data['lang']))
            return
        if props.__eq__("prev"):
            data['page'] -= 1
            text = translate(data['lang'], 'THE_ONE_BACK')
            await CreateBronState.reply_products.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=all_product_inline(page=data['page'], token=data['token'],
                                                                                lang=data['lang']))
            return
        if props.__eq__("next"):
            data['page'] += 1
            text = translate(data['lang'], 'THE_ONE_NEXT')
            await CreateBronState.reply_products.set()
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
            text = f"{translate(data['lang'], 'NAME')}:\t\t{name}\n{translate(data['lang'], 'CONTENT')}:\t\t{composition}\n{translate(data['lang'], 'ORIGINAL_COUNT')}:\t\t{original_count}\n{translate(data['lang'], 'PRICE50%')}:\t\t{price_split(price1)} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'PRICE100%')}:\t\t{price_split(price2)} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'EXPIRATION_DATE')}:\t\t{expiration_date}\n{translate(data['lang'], 'SERIA')}\t\t{seria}\n{translate(data['lang'], 'STATUS')}:\t\t{active}\n{translate(data['lang'], 'CHOICE_COUNT')}:\t\t"
            await CreateBronState.count.set()
            if not image:
                await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                    reply_markup=create_count())
            else:
                try:
                    await call.message.bot.send_photo(caption=text, photo=image, chat_id=call.message.chat.id,
                                                      reply_markup=create_count())
                except Exception:
                    import os
                    image_path = os.path.join(PRODUCT_IMAGE, f"{image}.jpg")
                    await call.message.bot.send_photo(caption=text, chat_id=call.message.chat.id,
                                                      photo=(open(image_path, 'rb')), reply_markup=create_count())
            return
        text = translate(data['lang'], 'PRODUCT_NO_ACTIVE')
        await CreateBronState.products.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=all_product_inline(page=data['page'], token=data['token'],
                                                                            lang=data['lang']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=CreateBronState.count)
async def create_product_count_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                try:
                    price = int(message.text)
                except Exception:
                    await message.delete()
                    return
                get_product = get_one_product(data['product'], token=data['token'])
                if price <= get_product['count']:
                    dict_product = {"product": data["product_id"], "name": data['name'],
                                    "composition": data['composition'],
                                    "active": data['active'],
                                    "count_product": data['count_product'],
                                    "original_count": data['original_count'], "size": data['size'],
                                    "expiration_date": data['expiration_date'],
                                    "price1": data['price1'], "price2": data['price2'], "seria": data['seria'],
                                    "count": price}
                    in_product = False
                    number = 0
                    old_product = 0
                    for i, product in enumerate(data['products_dict']):
                        if product['product'] == dict_product['product']:
                            in_product = True
                            number = i
                    if in_product:
                        if price > data['count_product'] or price < 0:
                            text = translate(data['lang'], 'NOT_FOUND_WAREHOUSE_PRODUCT')
                            await CreateBronState.count.set()
                            await message.bot.send_message(text=text, chat_id=message.chat.id)
                            return
                        old_product = data['products_dict'][number]['count']
                        data['products_dict'][number]['count'] = price
                        get_product = get_one_product(data['product'], token=data['token'])
                        data['all_price1'] -= old_product * get_product['price1']
                        data['all_price2'] -= old_product * get_product['price2']
                    else:
                        data['products_dict'].append(dict_product)
                    data['count'] = price
                    get_product = get_one_product(data['product'], token=data['token'])
                    data['price1'] = get_product['price1'] * data['count']
                    data['price2'] = get_product['price2'] * data['count']
                    if not in_product:
                        data['products'].append(
                            {"product": data['product'], "product_name": get_product["name"], "count": data['count'],
                             'price1': data['price1'],
                             "price2": data['price2']})
                    else:
                        data['products'][number]['count'] += data['count']
                        data['products'][number]['price1'] = data['price1']
                        data['products'][number]['price2'] = data['price2']
                    data['all_price1'] += data['price1']
                    data['all_price2'] += data['price2']
                    price1 = price_split(data['price1'])
                    price2 = price_split(data['price2'])
                    all_price1 = price_split(data['all_price1'])
                    all_price2 = price_split(data['all_price2'])
                    text = f"{translate(data['lang'], 'NAME')}:\t\t{data['name']}\n{translate(data['lang'], 'CONTENT')}:\t\t{data['composition']}\n{translate(data['lang'], 'ORIGINAL_COUNT')}:\t\t{data['original_count']}\n{translate(data['lang'], 'PRICE50%')}:\t\t{price1} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'PRICE100%')}:\t\t{price2} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'EXPIRATION_DATE')}:\t\t{data['expiration_date']}\n{translate(data['lang'], 'SERIA')}\t\t{data['seria']}\n{translate(data['lang'], 'STATUS')}:\t\t{data['active']}\n"
                    text += f"{translate(data['lang'], 'TOTAL_PRICE50%')}:\t\t{all_price1} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'TOTAL_PRICE100%')}: \t\t{all_price2} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'SAVE_BASKET')}"
                    await CreateBronState.check.set()
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
                text = translate(data['lang'], 'BAD_REQUEST_PRODUCT')
                await CreateBronState.count.set()
                await message.bot.send_message(text=text, chat_id=message.chat.id)
                return
            async with state.proxy() as data:
                text = translate(data['lang'], 'CHOICE_PRODUCT')
                await CreateBronState.products.set()
                await message.bot.send_message(text=text, chat_id=message.chat.id,
                                               reply_markup=all_product_inline(page=data['page'],
                                                                               token=data['token'],
                                                                               lang=data['lang']))
                return
        async with state.proxy() as data:
            text = translate(data['lang'], 'BACK')
            await BaseState.base.set()
            user = get_one_user(data['user_id'])
            data['role'] = user['role']
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=base_menu(data['lang'], data['role']))
        return


@dp.callback_query_handler(state=CreateBronState.count)
async def create_product_count_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data.__eq__('exit'):
            async with state.proxy() as data:
                text = translate(data['lang'], 'BACK')
                await BronState.begin.set()
                await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                    reply_markup=company_all_inline(data['search'],
                                                                                    data['token'],
                                                                                    data['lang']))
            return
        price = call.data[1:]
        price = int(price)
        get_product = get_one_product(data['product'], token=data['token'])
        if price <= get_product['count']:
            dict_product = {"product": data["product_id"], "name": data['name'], "composition": data['composition'],
                            "active": data['active'],
                            "count_product": data['count_product'],
                            "original_count": data['original_count'], "size": data['size'],
                            "expiration_date": data['expiration_date'],
                            "price1": data['price1'], "price2": data['price2'], "seria": data['seria'],
                            "count": price}
            in_product = False
            number = 0
            old_product = 0
            for i, product in enumerate(data['products_dict']):
                if product['product'] == dict_product['product']:
                    in_product = True
                    number = i
            if in_product:
                if price > data['count_product'] or price < 0:
                    text = translate(data['lang'], 'NOT_FOUND_WAREHOUSE_PRODUCT')
                    await CreateBronState.count.set()
                    await call.bot.send_message(text=text, chat_id=call.message.chat.id, reply_markup=create_count())
                    return
                old_product = data['products_dict'][number]['count']
                data['products_dict'][number]['count'] = price
                get_product = get_one_product(data['product'], token=data['token'])
                data['all_price1'] -= old_product * get_product['price1']
                data['all_price2'] -= old_product * get_product['price2']
            else:
                if price > data['count_product'] or price < 0:
                    text = translate(data['lang'], 'NOT_FOUND_WAREHOUSE_PRODUCT')
                    await CreateBronState.count.set()
                    await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                        reply_markup=create_count())
                    return
                data['products_dict'].append(dict_product)
            data['count'] = price
            get_product = get_one_product(data['product'], token=data['token'])
            data['price1'] = get_product['price1'] * data['count']
            data['price2'] = get_product['price2'] * data['count']
            if not in_product:
                data['products'].append(
                    {"product": data['product'], "product_name": get_product["name"], "count": data['count'],
                     'price1': data['price1'],
                     "price2": data['price2']})
            else:
                data['products'][number]['count'] += data['count']
                data['products'][number]['price1'] = data['price1']
                data['products'][number]['price2'] = data['price2']
            data['all_price1'] += data['price1']
            data['all_price2'] += data['price2']
            price1 = price_split(data['price1'])
            price2 = price_split(data['price2'])
            all_price1 = price_split(data['all_price1'])
            all_price2 = price_split(data['all_price2'])
            text = f"{translate(data['lang'], 'NAME')}:\t\t{data['name']}\n{translate(data['lang'], 'CONTENT')}:\t\t{data['composition']}\n{translate(data['lang'], 'ORIGINAL_COUNT')}:\t\t{data['original_count']}\n{translate(data['lang'], 'PRICE50%')}:\t\t{price1} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'PRICE100%')}:\t\t{price2} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'EXPIRATION_DATE')}:\t\t{data['expiration_date']}\n{translate(data['lang'], 'SERIA')}\t\t{data['seria']}\n{translate(data['lang'], 'STATUS')}:\t\t{data['active']}\n"
            text += f"{translate(data['lang'], 'TOTAL_PRICE50%')}:\t\t{all_price1} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'TOTAL_PRICE100%')}: \t\t{all_price2} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'SAVE_BASKET')}"
            await CreateBronState.check.set()
            if not data['image']:
                await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                    reply_markup=choice_product(data['lang']))
            else:
                try:
                    await call.message.bot.send_photo(caption=text, photo=data['image'], chat_id=call.message.chat.id,
                                                      reply_markup=choice_product(data['lang']))
                except Exception:
                    import os
                    image_path = os.path.join(PRODUCT_IMAGE, f"{data['image']}.jpg")
                    await call.message.bot.send_photo(caption=text, chat_id=call.message.chat.id,
                                                      photo=(open(image_path, 'rb')),
                                                      reply_markup=choice_product(data['lang']))
            return
        text = translate(data['lang'], 'BAD_REQUEST_PRODUCT')
        await CreateBronState.count.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id)
        return


@dp.callback_query_handler(state=CreateBronState.check)
async def check_warehouse_handler(call: types.CallbackQuery, state: FSMContext):
    props = call.data
    async with state.proxy() as data:
        if props.__eq__("no"):
            text = translate(data['lang'], 'THE_BACK')
            await CreateBronState.products.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=all_product_inline(page=data['page'], token=data['token'],
                                                                                lang=data['lang']))
            return

        all_price1 = price_split(data['all_price1'])
        all_price2 = price_split(data['all_price2'])
        text = ""
        for i, product in enumerate(data['products_dict'], start=1):
            price1 = price_split(product['price1'] * product['count'])
            price2 = price_split(product['price2'] * product['count'])
            text += f"{i}\n{translate(data['lang'], 'NAME')}\t\t{product['name']}\n{translate(data['lang'], 'COUNT')}:\t\t{product['count']}\n{translate(data['lang'], 'PRICE50%')}:\t\t{price1} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'PRICE100%')}:\t\t{price2} {translate(data['lang'], 'SUM')}\n\n"
        text += f"{translate(data['lang'], 'TOTAL_PRICE50%')}:\t\t{all_price1} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'TOTAL_PRICE100%')}:\t\t{all_price2} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'CHOICE_REPLY')}"
        await CreateBronState.choice_product_reply.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=check_basket(data['lang']))


@dp.message_handler(lambda message: (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
    russian['BACK_MENU']) or message.text.__eq__(
    translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                                            not str(message.text).__eq__('/start')), state=CreateBronState.check)
async def create_product_back_menu_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = f"{translate(data['lang'], 'NAME')}:\t\t{data['name']}\n{translate(data['lang'], 'CONTENT')}:\t\t{data['composition']}\n{translate(data['lang'], 'ORIGINAL_COUNT')}:\t\t{data['original_count']}\n{translate(data['lang'], 'PRICE50%')}:\t\t{price_split(data['price1'])} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'PRICE100%')}:\t\t{price_split(data['price2'])} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'EXPIRATION_DATE')}:\t\t{data['expiration_date']}\n{translate(data['lang'], 'SERIA')}\t\t{data['seria']}\n{translate(data['lang'], 'STATUS')}:\t\t{data['active']}\n"
        text += f"{translate(data['lang'], 'TOTAL_PRICE50%')}:\t\t{price_split(data['all_price1'])} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'TOTAL_PRICE100%')}: \t\t{price_split(data['all_price2'])} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'SAVE_BASKET')}"
        await CreateBronState.check.set()
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
                await message.bot.send_photo(caption=text, chat_id=message.chat.id, photo=(open(image_path, 'rb')),
                                             reply_markup=choice_product(data['lang']))


@dp.callback_query_handler(state=CreateBronState.choice_product_reply)
async def choice_product_handler(call: types.CallbackQuery, state: FSMContext):
    props = call.data
    async with state.proxy() as data:
        if props.__eq__("no"):
            text = translate(data['lang'], 'CREATE_COMMENT')
            await CreateBronState.comment.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id)
        if props.__eq__("yes"):
            text = translate(data['lang'], 'CHOICE_PRODUCT')
            await CreateBronState.products.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=all_product_inline(page=data['page'], token=data['token'],
                                                                                lang=data['lang']))


@dp.message_handler(lambda message: not str(message.text).__eq__('/start'), state=CreateBronState.comment)
async def comment_create_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                data['order_comment'] = message.text
                products = data['products_dict']
                user_ = get_one_user(data['user_id'])
                name = user_['first_name']
                if user_['last_name']:
                    name = f"{user_['first_name']} {user_['last_name']}"
                district = district_retrieve(data['district'])
                text = f"{translate(data['lang'], 'CREATOR')}:\t{name}\n"
                for product in products:
                    text += f"{translate(data['lang'], 'NAME')}: {product['name']}\n{translate(data['lang'], 'SUM50%')}: {price_split(product['price1'])}{translate(data['lang'], 'SUM')} * {translate(data['lang'], 'COUNT')} {product['count']}\n{translate(data['lang'], 'SUM100%')}:{price_split(product['price2'])}{translate(data['lang'], 'SUM')} * {translate(data['lang'], 'COUNT')} {product['count']}\n\n"
                data['products'] = products
                all_price1 = price_split(data['all_price1'])
                all_price2 = price_split(data['all_price2'])
                text += f"{translate(data['lang'], 'DISTRICT')}:\t{district['name']}\n"
                text += f"{translate(data['lang'], 'INN_GET')}:\t{data['order_inn']}\n"
                text += f"{translate(data['lang'], 'COMPANY_NAME')}:\t{data['companyName']}\n"
                text += f"{translate(data['lang'], 'COMPANY_PHONE')}:\t{data['companyPhone'] or translate(data['lang'], 'NOT_FOUND')}\n"
                text += f"{translate(data['lang'], 'COMMENT_GET')}:\t{data['order_comment']}\n\n"
                text += f"{translate(data['lang'], 'TOTAL_PRICE50%')} :\t{all_price1} {translate(data['lang'], 'SUM')}\n"
                text += f"{translate(data['lang'], 'TOTAL_PRICE100%')} :\t{all_price2} {translate(data['lang'], 'SUM')}\n"
                text += f"{translate(data['lang'], 'CREATED_DATE')} : \t{str(datetime.now())[0:19]}\n"
                await BronState.final_create.set()
                await message.bot.send_message(text=text, chat_id=message.chat.id,
                                               reply_markup=choice_price_markup(all_price1, all_price2,
                                                                                data['lang']))
                return
            text = translate(data['lang'], 'CREATE_COMMENT')
            await CreateBronState.comment.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id)
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.callback_query_handler(state=BronState.final_create)
async def final_create_handler(call: types.CallbackQuery, state: FSMContext):
    props = call.data
    async with state.proxy() as data:
        if props.__eq__("no"):
            text = translate(data['lang'], 'NO_SUCCESS')
            await BronState.bron.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=bron_menu(data['lang']))
            return
        total_price = 0
        if props.__eq__("price1"):
            data['type_price'] = "50%"
            total_price = price_split(data['all_price1'])
        elif props.__eq__("price2"):
            data['type_price'] = "100%"
            total_price = price_split(data['all_price2'])
        text = f"{translate(data['lang'], 'COMPANY_NAME')}: {data['companyName']}\nInn:{data['order_inn']}\n\t\t\t\t\t\t{translate(data['lang'], 'BASKET')}\n"
        for i, product in enumerate(data['products_dict'], start=1):
            text += f"{i}){translate(data['lang'], 'NAME')}: {product['name']}\n{translate(data['lang'], 'COUNT')}: {product['count']}\n{translate(data['lang'], 'PRICE')}({data['type_price']}):{price_split(product['price1'] * product['count']) if data['type_price'].__eq__('50%') else price_split(product['price2'] * product['count'])} {translate(data['lang'], 'SUM')}\n\n"
        text += f"{translate(data['lang'], 'TOTAL_PRICE')}({data['type_price']}): {total_price} {translate(data['lang'], 'SUM')}\n\n"
        text += translate(data['lang'], 'SEND_MANAGER')
        await BronState.manager_send.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=check_basket(data['lang']))


@dp.callback_query_handler(state=BronState.manager_send)
async def create_send_manager_handler(call: types.CallbackQuery, state: FSMContext):
    props = call.data
    send_manager = True
    if props.__eq__("no"):
        send_manager = False
    async with state.proxy() as data:
        total_price = 0
        if str(data['type_price']).__eq__("50%"):
            total_price = data['all_price1']
        if str(data['type_price']).__eq__("100%"):
            total_price = data['all_price2']
        products = []
        for i in data['products_dict']:
            products.append(
                {"product": i['product'], "count": i['count'],
                 "price": i['price1'] * i['count'] if data['type_price'].__eq__("50%") else i['price2'] * i[
                     'count']})
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
            update_product(name=name, composition=composition, count=count, original_count=original_count,
                           price1=price1,
                           price2=price2, expired_date=expiration_date, seria=seria,
                           active=product_one.get("active"),
                           image=image,
                           product_id=product, token=data['token'],
                           created_by=product_one.get('created_by'))
        user = get_chat_id(chat_id=call.message.chat.id)
        order_create(products=products, inn=data['order_inn'], comment=data['order_comment'],
                     total_price=total_price, is_manager_send=send_manager, token=user['token'],
                     type_price=data['type_price'], company_name=data['companyName'],
                     phone_number=data['companyPhone'],
                     company_address=data['companyAddress'], bank_name=data['companyBank'], status=send_manager)
        if send_manager:
            managers = get_office_managers()
            district = district_retrieve(user['district'])
            name = user['first_name']
            if user['last_name']:
                name = f"{user['first_name']} {user['last_name']}"
            for manager in managers:
                text2 = f"{translate(data['lang'], 'COMPANY_NAME')}: {data['companyName']}\nInn: {data['order_inn']}\n{translate(data['lang'], 'CREATOR')}: {name}\n{translate(data['lang'], 'DISTRICT')}: {translate_cyrillic_or_latin(district['name'], data['lang'])}\n\t\t\t\t\t\t{translate(data['lang'], 'BASKET')}\n"
                for i, product in enumerate(data['products_dict'], start=1):
                    text2 += f"{i}){translate(data['lang'], 'NAME')}: {product['name']}\n{translate(data['lang'], 'COUNT')}: {product['count']}\n{translate(data['lang'], 'PRICE')}({data['type_price']}):{price_split(product['price1'] * product['count']) if data['type_price'].__eq__('50%') else price_split(product['price2'] * product['count'])} {translate(data['lang'], 'SUM')}\n\n"
                text2 += f"{translate(data['lang'], 'TOTAL_PRICE')}({data['type_price']}): {total_price} {translate(data['lang'], 'SUM')}\n\n"
                await call.message.bot.send_message(text=text2, chat_id=manager['chat_id'])
        text = translate(data['lang'], 'SUCCESS')
        await BronState.bron.set()
        await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                            reply_markup=bron_menu(data['lang']))


@dp.message_handler(lambda message: (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
    russian['HOME_BACK']) or str(message.text).__eq__(translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))) and (
                                            not str(message.text).__eq__('/start')),
                    state='*')
async def home_menu_back_menu_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))
