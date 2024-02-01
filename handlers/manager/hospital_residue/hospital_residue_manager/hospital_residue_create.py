from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import russian, latin
from api.orders import order_get_one_order
from api.orders.company import Company
from api.product import get_one_product
from api.users.users import get_one_user
from button.inline import company_all_inline, product_reply_markup, check_basket
from button.reply_markup import back_menu, base_menu
from dispatch import dp
from states import BaseState, ManagerIncomeState, HospitalResidueState, CreateCompanyBossesState, ProductResidueState
from utils.number_split_for_price import price_split

#
# @dp.message_handler(lambda message: (message.text.__eq__(russian['HOSPITAL_RESIDUE']) or message.text.__eq__(
#     latin['HOSPITAL_RESIDUE']) or message.text.__eq__(
#     translate_cyrillic_or_latin(latin['HOSPITAL_RESIDUE'], 'cyr'))) and (
#                                             not str(message.text).__eq__('/start')),
#                     state=BaseState.base)
# async def agent_debit_menu(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['product_list'] = []
#         data['page'] = 1
#         data['search'] = None
#         text = translate(data['lang'], 'CHOICE_COMPANY')
#         text2 = translate(data['lang'], 'OR_SEARCH')
#         await HospitalResidueState.begin.set()
#         await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
#         await message.bot.send_message(text=text2, chat_id=message.chat.id,
#                                        reply_markup=company_all_inline(data['page'], data['search'], data['token'],
#                                                                        data['lang']))
#
#
# @dp.callback_query_handler(state=HospitalResidueState.begin)
# async def cal_company_state_message_handler(call: types.CallbackQuery, state: FSMContext):
#     props = call.data
#     async with state.proxy() as data:
#         if props.__eq__("prev"):
#             data['page'] -= 1
#             text = translate(data['lang'], 'THE_ONE_BACK')
#             await HospitalResidueState.begin.set()
#             await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
#                                                 reply_markup=company_all_inline(data['page'], data['search'],
#                                                                                 data['token'],
#                                                                                 data['lang']))
#             return
#         if props.__eq__("next"):
#             data['page'] += 1
#             text = translate(data['lang'], 'THE_ONE_NEXT')
#             await HospitalResidueState.begin.set()
#             await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
#                                                 reply_markup=company_all_inline(data['page'], data['search'],
#                                                                                 data['token'],
#                                                                                 data['lang']))
#             return
#         if props.__eq__('new'):
#             text = translate(data['lang'], 'CREATE_COMPANY_INN')
#             await HospitalResidueState.inn.set()
#             await call.message.bot.send_message(text=text, chat_id=call.message.chat.id)
#             return
#         if props.__eq__("back"):
#             text = translate(data['lang'], 'BACK')
#             await BaseState.base.set()
#             await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
#                                                 reply_markup=base_menu(data['lang'], data['role']))
#             return
#         data['company_id'] = props[1:]
#         company = Company(company_id=props[1:], token=data['token']).get_one()
#         if company.get('company_name'):
#             data['companyName'] = company['company_name']
#         if company.get('phone_number'):
#             data["companyPhone"] = company['phone_number']
#         if company.get('company_address'):
#             data['companyAddress'] = company['company_address']
#         if company.get('bank_name'):
#             data['companyBank'] = company['bank_name']
#         if company.get('inn'):
#             data['order_inn'] = company['inn']
#         if not company.get('company_director_name'):
#             text = translate(data['lang'], 'CREATE_DIRECTOR_NAME')
#             await CreateCompanyBossesState.director_name.set()
#             await call.message.bot.send_message(chat_id=call.message.chat.id, text=text)
#         else:
#             data['order_id'] = call.data[1:]
#             order_one = order_get_one_order(order_id=data['order_id'], token=data['token'])
#             is_manager_send = ""
#             if order_one['status'].__eq__('office_manager'):
#                 is_manager_send = translate_cyrillic_or_latin("Offis Menedjerda", data['lang'])
#             elif order_one['status'].__eq__('delivery'):
#                 is_manager_send = translate_cyrillic_or_latin("Omborxonada", data['lang'])
#             elif order_one['status'].__eq__('supplier'):
#                 is_manager_send = translate_cyrillic_or_latin("Yetkazib beruvchida", data['lang'])
#             if order_one['status'] is None:
#                 is_manager_send = translate_cyrillic_or_latin('MP/Menedjerda', data['lang'])
#             seller = get_one_user(order_one['seller'])
#             name = f"{seller['first_name']}"
#             first_list = []
#             all_product_list = []
#             if seller['last_name']:
#                 name = f"{seller['first_name']} {seller['last_name']}"
#             text = f"{translate(data['lang'], 'COMPANY_NAME')}:{order_one.get('company_name')}\n{translate(data['lang'], 'INN_GET')}: {order_one.get('inn')}\n{translate(data['lang'], 'COMMENT_GET')}:{order_one.get('comment')}\n{translate(data['lang'], 'CREATOR')}: {translate_cyrillic_or_latin(name, data['lang'])}\n\n"
#             for i, product in enumerate(order_one.get("products"), start=1):
#                 product_one = get_one_product(product_id=product.get("product"), token=data['token'])
#                 all_product_dict = {"name": product_one.get('name'),
#                                     'id': product.get('product'),
#                                     'count': product.get('count'),
#                                     'price': int(product.get('price'))
#                                     }
#                 first_dict = {'name': product_one.get('name'), 'id': product.get('product')}
#                 text += f"{i}){translate(data['lang'], 'NAME')}:{product_one.get('name')}\n{translate(data['lang'], 'COUNT')}:{price_split(product.get('count'))}\n{translate(data['lang'], 'PRICE')}({order_one.get('type_price')}):{price_split(product.get('price'))} {translate(data['lang'], 'SUM')}\n\n"
#                 all_product_list.append(all_product_dict)
#                 data['all_product_list'] = all_product_list
#                 first_list.append(first_dict)
#             data['first_list'] = first_list
#             text += f"\n{translate(data['lang'], 'CREATED_DATE')}:{str(order_one['created_date'][:10]) + ' ' + order_one['created_date'][11:16]}\n{translate(data['lang'], 'TOTAL_PRICE')}({order_one.get('type_price')}):{price_split(order_one.get('total_price'))} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'CREATE_PRODUCT_STATUS')} : {is_manager_send}\n"
#             await ProductResidueState.begin.set()
#             await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
#                                                 reply_markup=product_reply_markup(lang=data['lang'],
#                                                                                   product_list=first_list))
#
#
# @dp.message_handler(
#     lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
#         russian['BACK_MENU']) or str(
#         message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
#                             not str(message.text).__eq__('/start')),
#     state=[HospitalResidueState.begin])
# async def back_menu_handler(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         text = translate(data['lang'], 'BASE_MENU_BACK')
#         await BaseState.base.set()
#         await message.bot.send_message(text=text, chat_id=message.chat.id,
#                                        reply_markup=base_menu(data['lang'], data['role']))
#
#
# @dp.message_handler(
#     lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
#         russian['BACK_MENU']) or str(
#         message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
#                             not str(message.text).__eq__('/start')),
#     state=[ProductResidueState.begin])
# async def back_menu_handler(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         text = translate(data['lang'], 'BASE_MENU_BACK')
#         await HospitalResidueState.begin.set()
#         await message.bot.send_message(text=text, chat_id=message.chat.id,
#                                        reply_markup=company_all_inline(data['page'], data['search'], data['token'],
#                                                                        data['lang']))
#
#
# @dp.callback_query_handler(state=ProductResidueState.begin)
# async def product_residue_state(call: types.CallbackQuery, state: FSMContext):
#     async with state.proxy() as data:
#         data['product_residue'] = call.data[1:]
#         text = translate(data['lang'], 'CHOICE_COUNT_UPDATE')
#         await ProductResidueState.product.set()
#         await call.message.bot.send_message(text=text, chat_id=call.message.chat.id)
#
#
# @dp.message_handler(state=ProductResidueState.product)
# async def product_count_send_handler(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         if message.text != '/start':
#             try:
#                 count = int(message.text)
#             except:
#                 await message.delete()
#             for number, i in enumerate(data['all_product_list']):
#                 if int(data['product_residue']) == i['id']:
#                     p = i['count']
#                     data['all_product_list'][number]['count'] = int(message.text)
#                     data['all_product_list'][number]['price'] = int((i['price'] / p) * i['count'])
#             order_one = order_get_one_order(order_id=data['order_id'], token=data['token'])
#             is_manager_send = ""
#             if order_one['status'].__eq__('office_manager'):
#                 is_manager_send = translate_cyrillic_or_latin("Offis Menedjerda", data['lang'])
#             elif order_one['status'].__eq__('delivery'):
#                 is_manager_send = translate_cyrillic_or_latin("Omborxonada", data['lang'])
#             elif order_one['status'].__eq__('supplier'):
#                 is_manager_send = translate_cyrillic_or_latin("Yetkazib beruvchida", data['lang'])
#             if order_one['status'] is None:
#                 is_manager_send = translate_cyrillic_or_latin('MP/Menedjerda', data['lang'])
#             seller = get_one_user(order_one['seller'])
#             name = f"{seller['first_name']}"
#             if seller['last_name']:
#                 name = f"{seller['first_name']} {seller['last_name']}"
#             text = f"{translate(data['lang'], 'COMPANY_NAME')}:{order_one.get('company_name')}\n{translate(data['lang'], 'INN_GET')}: {order_one.get('inn')}\n{translate(data['lang'], 'COMMENT_GET')}:{order_one.get('comment')}\n{translate(data['lang'], 'CREATOR')}: {translate_cyrillic_or_latin(name, data['lang'])}\n\n"
#             summa = 0
#             for i, product in enumerate(data['all_product_list'], start=1):
#                 summa += product['price']
#                 text += f"{i}){translate(data['lang'], 'NAME')}:{product.get('name')}\n{translate(data['lang'], 'COUNT')}:{price_split(product.get('count'))}\n{translate(data['lang'], 'PRICE')}:{price_split(product.get('price'))}\n\n"
#
#             text += f"\n{translate(data['lang'], 'CREATED_DATE')}:{str(order_one['created_date'][:10]) + ' ' + order_one['created_date'][11:16]}\n{translate(data['lang'], 'TOTAL_PRICE')}({order_one.get('type_price')}):{price_split(summa)} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'CREATE_PRODUCT_STATUS')} : {is_manager_send}\n{translate(data['lang'], 'CHOICE_REPLY')}\n"
#             await ProductResidueState.reply_product.set()
#             await message.bot.send_message(text=text, chat_id=message.chat.id,
#                                            reply_markup=check_basket(data['lang']))
#         else:
#             text = translate(data['lang'], "BASE_MENU")
#             await BaseState.base.set()
#             await message.bot.send_message(text=text, chat_id=message.chat.id,
#                                            reply_markup=base_menu(data['lang'], data['role']))
#
#
# @dp.callback_query_handler(state=ProductResidueState.reply_product)
# async def reply_product_hospital_handler(call: types.CallbackQuery, state: FSMContext):
#     async with state.proxy() as data:
#         if call.data.__eq__('yes'):
#             order_one = order_get_one_order(order_id=data['order_id'], token=data['token'])
#             is_manager_send = ""
#             if order_one['status'].__eq__('office_manager'):
#                 is_manager_send = translate_cyrillic_or_latin("Offis Menedjerda", data['lang'])
#             elif order_one['status'].__eq__('delivery'):
#                 is_manager_send = translate_cyrillic_or_latin("Omborxonada", data['lang'])
#             elif order_one['status'].__eq__('supplier'):
#                 is_manager_send = translate_cyrillic_or_latin("Yetkazib beruvchida", data['lang'])
#             if order_one['status'] is None:
#                 is_manager_send = translate_cyrillic_or_latin('MP/Menedjerda', data['lang'])
#             seller = get_one_user(order_one['seller'])
#             name = f"{seller['first_name']}"
#             if seller['last_name']:
#                 name = f"{seller['first_name']} {seller['last_name']}"
#             text = f"{translate(data['lang'], 'COMPANY_NAME')}:{order_one.get('company_name')}\n{translate(data['lang'], 'INN_GET')}: {order_one.get('inn')}\n{translate(data['lang'], 'COMMENT_GET')}:{order_one.get('comment')}\n{translate(data['lang'], 'CREATOR')}: {translate_cyrillic_or_latin(name, data['lang'])}\n\n"
#             summa = 0
#             for i, product in enumerate(data['all_product_list'], start=1):
#                 summa += product['price']
#                 text += f"{i}){translate(data['lang'], 'NAME')}:{product.get('name')}\n{translate(data['lang'], 'COUNT')}:{price_split(product.get('count'))}\n{translate(data['lang'], 'PRICE')}:{price_split(product.get('price'))}\n\n"
#             text += f"\n{translate(data['lang'], 'CREATED_DATE')}:{str(order_one['created_date'][:10]) + ' ' + order_one['created_date'][11:16]}\n{translate(data['lang'], 'TOTAL_PRICE')}({order_one.get('type_price')}):{price_split(summa)} {translate(data['lang'], 'SUM')}\n{translate(data['lang'], 'CREATE_PRODUCT_STATUS')} : {is_manager_send}\n{translate(data['lang'], 'CHOICE_REPLY')}\n"
#             await ProductResidueState.begin.set()
#             await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
#                                                 reply_markup=product_reply_markup(lang=data['lang'],
#                                                                                   product_list=data['first_list']))
#         else:
#             pass
