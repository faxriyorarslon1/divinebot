from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import russian, latin
from api.orders import order_get_one_order
from api.orders.company import Company
from api.orders.hospital_residue import HospitalResidue
from api.product import get_one_product
from api.users.users import get_one_user
from button.inline import company_all_inline, product_reply_markup, check_basket
from button.reply_markup import back_menu, base_menu, manager_hospital_residue
from dispatch import dp
from states import BaseState, ManagerIncomeState, HospitalResidueState, CreateCompanyBossesState, ProductResidueState, \
    ManagerHospitalVizit, HospitalResidueManagerState, CreateCompanyBossesManagerState, ProductResidueManagerState


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['EXCEL_TEXT']) or str(message.text).__eq__(
        russian['EXCEL_TEXT']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['EXCEL_TEXT'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')), state=ManagerHospitalVizit.begin)
async def manager_pharmacy_residue_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['aknel_gel'] = 0
        data['astarakson_1125'] = 0
        data['astarakson_562'] = 0
        data['astaryus'] = 0
        data['intrizol'] = 0
        data['livomed_tab'] = 0
        data['livomed_sirop'] = 0
        data['renum_cap'] = 0
        data['stresson_cap'] = 0
        data['tavamed'] = 0
        data['x_payls_maz'] = 0
        data['seprazon'] = 0
        data['entro_d_cap'] = 0
        data['entro_d_sashe'] = 0
        data['lamino_100'] = 0
        data['lamino_200'] = 0
        data['page'] = 1
        data['search'] = None
        text = translate(data['lang'], 'CHOICE_COMPANY')
        text2 = translate(data['lang'], 'OR_SEARCH')
        await HospitalResidueManagerState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
        await message.bot.send_message(text=text2, chat_id=message.chat.id,
                                       reply_markup=company_all_inline(data['page'], data['search'], data['token'],
                                                                       data['lang']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[HospitalResidueManagerState.begin])
async def back_menu_base_menu_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'CHOICE_EXCEL_OR_HOSPITAL_VIZIT_RESIDUE')
        await ManagerHospitalVizit.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=manager_hospital_residue(data['lang']))


@dp.callback_query_handler(state=HospitalResidueManagerState.begin)
async def cal_company_state_message_handler(call: types.CallbackQuery, state: FSMContext):
    props = call.data
    async with state.proxy() as data:
        if props.__eq__("prev"):
            data['page'] -= 1
            text = translate(data['lang'], 'THE_ONE_BACK')
            await HospitalResidueManagerState.begin.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=company_all_inline(data['page'], data['search'],
                                                                                data['token'],
                                                                                data['lang']))
            return
        if props.__eq__("next"):
            data['page'] += 1
            text = translate(data['lang'], 'THE_ONE_NEXT')
            await HospitalResidueManagerState.begin.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=company_all_inline(data['page'], data['search'],
                                                                                data['token'],
                                                                                data['lang']))
            return
        if props.__eq__('new'):
            text = translate(data['lang'], 'CREATE_COMPANY_INN')
            await HospitalResidueManagerState.inn.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id)
            return
        if props.__eq__("back"):
            text = translate(data['lang'], 'BACK')
            await BaseState.base.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=base_menu(data['lang'], data['role']))
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
        if not company.get('company_director_name'):
            text = translate(data['lang'], 'CREATE_DIRECTOR_NAME')
            await CreateCompanyBossesManagerState.director_name.set()
            await call.message.bot.send_message(chat_id=call.message.chat.id, text=text)
        else:
            data['order_id'] = call.data[1:]
            order_one = HospitalResidue(company=call.data[1:], token=data['token']).hospital_user_vizit()
            if order_one:
                data['order'] = order_one[0]['id']
                is_manager_send = ""
                if order_one[0]['status'].__eq__('office_manager'):
                    is_manager_send = translate_cyrillic_or_latin("Offis Menedjerda", data['lang'])
                elif order_one[0]['status'].__eq__('delivery'):
                    is_manager_send = translate_cyrillic_or_latin("Omborxonada", data['lang'])
                elif order_one[0]['status'].__eq__('supplier'):
                    is_manager_send = translate_cyrillic_or_latin("Yetkazib beruvchida", data['lang'])
                if order_one[0]['status'] is None:
                    is_manager_send = translate_cyrillic_or_latin('MP/Menedjerda', data['lang'])
                company_name = order_one[0]['company']['company_name']
                inn = order_one[0]['company']['inn']
                company_director_name = order_one[0]['company']['company_director_name']
                company_director_phone_number = order_one[0]['company']['company_director_phone_number']
                district = order_one[0]['district']['name']
                created_by = order_one[0]["created_by"]['first_name']
                if order_one[0]["created_by"]['last_name']:
                    created_by = f'{order_one[0]["created_by"]["first_name"]} {order_one[0]["created_by"]["last_name"]}'
                phone_number = order_one[0]['created_by']['phone_number']
                aknel_gel = order_one[0]['aknel_gel']
                data['aknel_gel'] = aknel_gel
                astarakson_1125 = order_one[0]['astarakson_1125']
                data['astarakson_1125'] = astarakson_1125
                astarakson_562 = order_one[0]['astarakson_562']
                data['astarakson_562'] = astarakson_562
                astaryus = order_one[0]['astaryus']
                data['astaryus'] = astaryus
                intrizol = order_one[0]['intrizol']
                data['intrizol'] = intrizol
                livomed_tab = order_one[0]['livomed_tab']
                data['livomed_tab'] = livomed_tab
                livomed_sirop = order_one[0]['livomed_sirop']
                data['livomed_sirop'] = livomed_sirop
                renum_cap = order_one[0]['renum_cap']
                data['renum_cap'] = renum_cap
                stresson_cap = order_one[0]['stresson_cap']
                data['stresson_cap'] = stresson_cap
                tavamed = order_one[0]['tavamed']
                data['tavamed'] = tavamed
                x_payls_maz = order_one[0]['x_payls_maz']
                data['x_payls_maz'] = x_payls_maz
                seprazon = order_one[0]['seprazon']
                data['seprazon'] = seprazon
                entro_d_cap = order_one[0]['entro_d_cap']
                data['entro_d_cap'] = entro_d_cap
                entro_d_sashe = order_one[0]['entro_d_sashe']
                data['entro_d_sashe'] = entro_d_sashe
                lamino_100 = order_one[0]['lamino_100']
                data['lamino_100'] = lamino_100
                lamino_200 = order_one[0]['lamino_200']
                data['lamino_200'] = lamino_200
                text = f"<b>{translate(data['lang'], 'COMPANY_NAME')}:{company_name}\n{translate(data['lang'], 'INN_GET')}:{inn}\n{translate(data['lang'], 'CREATOR')}: {translate_cyrillic_or_latin(created_by, data['lang'])}</b>\n\n"
                product_list = []
                if aknel_gel != 0:
                    text += f'{translate_cyrillic_or_latin("Акнель гель 10гр", data["lang"])}: {aknel_gel}\n'
                    product_list.append({'name': 'Акнель гель 10гр', 'id': 'aknel_gel'})
                if astarakson_1125 != 0:
                    product_list.append({"name": 'Астароксон TZ-1125', 'id': 'astarakson_1125'})
                    text += f'{translate_cyrillic_or_latin("Астароксон TZ-1125", data["lang"])}: {astarakson_1125}\n'
                if astarakson_562 != 0:
                    product_list.append({'name': 'Астароксон TZ-562,5', 'id': 'astarakson_562'})
                    text += f"{translate_cyrillic_or_latin('Астароксон TZ-562,5 ', data['lang'])}: {astarakson_562}\n"
                if astaryus != 0:
                    product_list.append({'name': 'Астарюс 20мг/мл амп. 5мл №5', 'id': 'astaryus'})
                    text += f"{translate_cyrillic_or_latin('Астарюс 20мг/мл амп. 5мл №5 ', data['lang'])}: {astaryus}\n"
                if intrizol != 0:
                    product_list.append({'name': 'Интризол крем 20гр', 'id': 'intrizol'})
                    text += f"{translate_cyrillic_or_latin('Интризол крем 20гр', data['lang'])}: {intrizol}\n"
                if livomed_tab != 0:
                    product_list.append({'name': 'Ливомед таб №60', 'id': 'livomed_tab'})
                    text += f"{translate_cyrillic_or_latin('Ливомед таб №60', data['lang'])}: {livomed_tab}\n"
                if livomed_sirop != 0:
                    product_list.append({'name': 'Ливомед сироп 200мл', 'id': 'livomed_sirop'})
                    text += f"{translate_cyrillic_or_latin('Ливомед сироп 200мл', data['lang'])}: {livomed_sirop}\n"
                if renum_cap != 0:
                    product_list.append({'name': 'Ренум капс. 250мг №60', 'id': "renum_cap"})
                    text += f"{translate_cyrillic_or_latin('Ренум капс. 250мг №60', data['lang'])}: {renum_cap}\n"
                if stresson_cap != 0:
                    product_list.append({'name': 'Стрессон капс №20', 'id': 'stresson_cap'})
                    text += f"{translate_cyrillic_or_latin('Стрессон капс №20', data['lang'])}:  {stresson_cap}\n"
                if tavamed != 0:
                    product_list.append({'name': 'ТАВАМЕД 500мг инфузия 100мл', 'id': 'tavamed'})
                    text += f"{translate_cyrillic_or_latin('ТАВАМЕД 500мг инфузия 100мл', data['lang'])}: {tavamed}\n"
                if x_payls_maz != 0:
                    product_list.append({'name': "Х-пайлс мазь 30г", 'id': "x_payls_maz"})
                    text += f"{translate_cyrillic_or_latin('Х-пайлс мазь 30г', data['lang'])} {x_payls_maz}\n"
                if seprazon != 0:
                    product_list.append({'name': 'Цепразон 1,5г', 'id': "seprazon"})
                    text += f"{translate_cyrillic_or_latin('Цепразон 1,5г', data['lang'])}: {seprazon}\n"
                if entro_d_cap != 0:
                    product_list.append({'name': "Энтро Д капс №10", 'id': "entro_d_cap"})
                    text += f"{translate_cyrillic_or_latin('Энтро Д капс №10 ', data['lang'])}: {entro_d_cap}\n"
                if entro_d_sashe != 0:
                    product_list.append({'name': "Энтро Д саше №10", 'id': "entro_d_sashe"})
                    text += f"{translate_cyrillic_or_latin('Энтро Д саше №10', data['lang'])}: {entro_d_sashe}\n"
                if lamino_100 != 0:
                    product_list.append({"name": "Ламино 100 мл", 'id': "lamino_100"})
                    text += f"{translate_cyrillic_or_latin('Ламино 100 мл', data['lang'])}: {lamino_100}\n"
                if lamino_200 != 0:
                    product_list.append({'name': "Ламино 200 мл", 'id': "lamino_200"})
                    text += f"{translate_cyrillic_or_latin('Ламино 200 мл ', data['lang'])}: {lamino_200}\n"
                text += f"\n{translate(data['lang'], 'CREATED_DATE')}:{str(order_one[0]['created_at'][:10]) + ' ' + order_one[0]['created_at'][11:16]}\n{translate(data['lang'], 'CREATE_PRODUCT_STATUS')} : {is_manager_send}\n"
                await ProductResidueManagerState.begin.set()
                await call.message.bot.send_message(text=text, chat_id=call.message.chat.id, parse_mode='HTML',
                                                    reply_markup=product_reply_markup(data['lang'],
                                                                                      product_list=product_list))
            else:
                company = Company(company_id=data['company_id'], token=data['token']).get_one()
                company_name = company['company_name']
                inn = company['inn']
                # company_director_name = order_one[0]['company']['company_director_name']
                # company_director_phone_number = order_one[0]['company']['company_director_phone_number']
                # district = data['district']
                created_by = data['first_name']
                # if data['last_name']:
                #     created_by = f'{order_one[0]["created_by"]["first_name"]} {order_one[0]["created_by"]["last_name"]}'
                # phone_number = order_one[0]['created_by']['phone_number']
                aknel_gel = data['aknel_gel']
                astarakson_1125 = data['astarakson_1125']
                astarakson_562 = data['astarakson_562']
                astaryus = data['astaryus']
                intrizol = data['intrizol']
                livomed_tab = data['livomed_tab']
                livomed_sirop = data['livomed_sirop']
                renum_cap = data['renum_cap']
                stresson_cap = data['stresson_cap']
                tavamed = data['tavamed']
                x_payls_maz = data['x_payls_maz']
                seprazon = data['seprazon']
                entro_d_cap = data['entro_d_cap']
                entro_d_sashe = data['entro_d_sashe']
                lamino_100 = data['lamino_100']
                lamino_200 = data['lamino_200']
                text = f"<b>{translate(data['lang'], 'COMPANY_NAME')}:{company_name}\n{translate(data['lang'], 'INN_GET')}:{inn}\n{translate(data['lang'], 'CREATOR')}: {translate_cyrillic_or_latin(created_by, data['lang'])}</b>\n\n"
                product_list = []
                # if aknel_gel == 0:
                text += f'{translate_cyrillic_or_latin("Акнель гель 10гр", data["lang"])}: {aknel_gel}\n'
                product_list.append({'name': 'Акнель гель 10гр', 'id': 'aknel_gel'})
                # if astarakson_1125 != 0:
                product_list.append({"name": 'Астароксон TZ-1125', 'id': 'astarakson_1125'})
                text += f'{translate_cyrillic_or_latin("Астароксон TZ-1125", data["lang"])}: {astarakson_1125}\n'
                product_list.append({'name': 'Астароксон TZ-562,5', 'id': 'astarakson_562'})
                text += f"{translate_cyrillic_or_latin('Астароксон TZ-562,5 ', data['lang'])}: {astarakson_562}\n"
                product_list.append({'name': 'Астарюс 20мг/мл амп. 5мл №5', 'id': 'astaryus'})
                text += f"{translate_cyrillic_or_latin('Астарюс 20мг/мл амп. 5мл №5 ', data['lang'])}: {astaryus}\n"
                product_list.append({'name': 'Интризол крем 20гр', 'id': 'intrizol'})
                text += f"{translate_cyrillic_or_latin('Интризол крем 20гр', data['lang'])}: {intrizol}\n"
                product_list.append({'name': 'Ливомед таб №60', 'id': 'livomed_tab'})
                text += f"{translate_cyrillic_or_latin('Ливомед таб №60', data['lang'])}: {livomed_tab}\n"
                product_list.append({'name': 'Ливомед сироп 200мл', 'id': 'livomed_sirop'})
                text += f"{translate_cyrillic_or_latin('Ливомед сироп 200мл', data['lang'])}: {livomed_sirop}\n"
                product_list.append({'name': 'Ренум капс. 250мг №60', 'id': "renum_cap"})
                text += f"{translate_cyrillic_or_latin('Ренум капс. 250мг №60', data['lang'])}: {renum_cap}\n"
                product_list.append({'name': 'Стрессон капс №20', 'id': 'stresson_cap'})
                text += f"{translate_cyrillic_or_latin('Стрессон капс №20', data['lang'])}:  {stresson_cap}\n"
                product_list.append({'name': 'ТАВАМЕД 500мг инфузия 100мл', 'id': 'tavamed'})
                text += f"{translate_cyrillic_or_latin('ТАВАМЕД 500мг инфузия 100мл', data['lang'])}: {tavamed}\n"
                product_list.append({'name': "Х-пайлс мазь 30г", 'id': "x_payls_maz"})
                text += f"{translate_cyrillic_or_latin('Х-пайлс мазь 30г', data['lang'])} {x_payls_maz}\n"
                product_list.append({'name': 'Цепразон 1,5г', 'id': "seprazon"})
                text += f"{translate_cyrillic_or_latin('Цепразон 1,5г', data['lang'])}: {seprazon}\n"
                product_list.append({'name': "Энтро Д капс №10", 'id': "entro_d_cap"})
                text += f"{translate_cyrillic_or_latin('Энтро Д капс №10 ', data['lang'])}: {entro_d_cap}\n"
                product_list.append({'name': "Энтро Д саше №10", 'id': "entro_d_sashe"})
                text += f"{translate_cyrillic_or_latin('Энтро Д саше №10', data['lang'])}: {entro_d_sashe}\n"
                product_list.append({"name": "Ламино 100 мл", 'id': "lamino_100"})
                text += f"{translate_cyrillic_or_latin('Ламино 100 мл', data['lang'])}: {lamino_100}\n"
                product_list.append({'name': "Ламино 200 мл", 'id': "lamino_200"})
                text += f"{translate_cyrillic_or_latin('Ламино 200 мл ', data['lang'])}: {lamino_200}\n"
                text += f"\n"
                await ProductResidueManagerState.begin.set()
                await call.message.bot.send_message(text=text, chat_id=call.message.chat.id, parse_mode='HTML',
                                                    reply_markup=product_reply_markup(data['lang'],
                                                                                      product_list=product_list))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[ProductResidueManagerState.begin])
async def back_menu_base_menu_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['search'] = None
        text = translate(data['lang'], 'CHOICE_COMPANY')
        text2 = translate(data['lang'], 'OR_SEARCH')
        await HospitalResidueManagerState.begin.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=back_menu(data['lang']))
        await message.bot.send_message(text=text2, chat_id=message.chat.id,
                                       reply_markup=company_all_inline(data['page'], data['search'], data['token'],
                                                                       data['lang']))


@dp.callback_query_handler(state=ProductResidueManagerState.begin)
async def call_back_product_choice_handler(call: types.CallbackQuery, state: FSMContext):
    props = call.data
    async with state.proxy() as data:
        data['product_pharmacy'] = props
        if props.__eq__('back'):
            text = translate(data['lang'], 'BACK')
            await HospitalResidueManagerState.begin.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=company_all_inline(data['page'], data['search'],
                                                                                data['token'],
                                                                                data['lang']))
        else:
            text = translate(data['lang'], 'CHOICE_COUNT_UPDATE')
            await ProductResidueManagerState.new_product.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id)


# @dp.message_handler(lambda message: message.text)
@dp.message_handler(state=ProductResidueManagerState.new_product)
async def pharmacy_residue_new_product_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.content_type == 'start':
            text = translate(data['lang'], 'BACK')
            await BaseState.base.set()
            user = get_one_user(data['user_id'])
            data['role'] = user['role']
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=base_menu(data['lang'], data['role']))
            return
        if not (str(message.text).__eq__(latin['HOME_BACK']) or str(message.text).__eq__(
                russian['HOME_BACK']) or str(message.text).__eq__(
            translate_cyrillic_or_latin(latin['HOME_BACK'], 'cyr'))):
            if not (message.text.__eq__(latin['BACK_MENU']) or message.text.__eq__(
                    russian['BACK_MENU']) or message.text.__eq__(
                translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))):
                try:
                    int(message.text)
                except:
                    text = translate(data['lang'], 'BAD_REQUEST')
                    await message.bot.send_message(text=text, chat_id=message.chat.id)
                    return
                props = data['product_pharmacy']
                if props.__eq__('aknel_gel'):
                    data['aknel_gel'] = message.text
                if props.__eq__('astarakson_1125'):
                    data['astarakson_1125'] = message.text
                if props.__eq__('astarakson_562'):
                    data['astarakson_562'] = message.text
                if props.__eq__("astaryus"):
                    data['astaryus'] = message.text
                if props.__eq__('intrizol'):
                    data['intrizol'] = message.text
                if props.__eq__('livomed_tab'):
                    data['livomed_tab'] = message.text
                if props.__eq__('livomed_sirop'):
                    data['livomed_sirop'] = message.text
                if props.__eq__('renum_cap'):
                    data['renum_cap'] = message.text
                if props.__eq__('stresson_cap'):
                    data['stresson_cap'] = message.text
                if props.__eq__('tavamed'):
                    data['tavamed'] = message.text
                if props.__eq__('x_payls_maz'):
                    data['x_payls_maz'] = message.text
                if props.__eq__('seprazon'):
                    data['seprazon'] = message.text
                if props.__eq__('entro_d_cap'):
                    data['entro_d_cap'] = message.text
                if props.__eq__('entro_d_sashe'):
                    data['entro_d_sashe'] = message.text
                if props.__eq__('lamino_100'):
                    data['lamino_100'] = message.text
                if props.__eq__('lamino_200'):
                    data['lamino_200'] = message.text
                text = translate(data['lang'], 'CHOICE_REPLY')
                await ProductResidueManagerState.reply_product.set()
                await message.bot.send_message(text=text, chat_id=message.chat.id,
                                               reply_markup=check_basket(data['lang']))
                return
            order_one = HospitalResidue(company=data['order_id'], token=data['token']).hospital_user_vizit()
            if order_one:
                data['order'] = order_one[0]['id']
                is_manager_send = ""
                if order_one[0]['status'].__eq__('office_manager'):
                    is_manager_send = translate_cyrillic_or_latin("Offis Menedjerda", data['lang'])
                elif order_one[0]['status'].__eq__('delivery'):
                    is_manager_send = translate_cyrillic_or_latin("Omborxonada", data['lang'])
                elif order_one[0]['status'].__eq__('supplier'):
                    is_manager_send = translate_cyrillic_or_latin("Yetkazib beruvchida", data['lang'])
                if order_one[0]['status'] is None:
                    is_manager_send = translate_cyrillic_or_latin('MP/Menedjerda', data['lang'])
                company_name = order_one[0]['company']['company_name']
                inn = order_one[0]['company']['inn']
                company_director_name = order_one[0]['company']['company_director_name']
                company_director_phone_number = order_one[0]['company']['company_director_phone_number']
                district = order_one[0]['district']['name']
                created_by = order_one[0]["created_by"]['first_name']
                if order_one[0]["created_by"]['last_name']:
                    created_by = f'{order_one[0]["created_by"]["first_name"]} {order_one[0]["created_by"]["last_name"]}'
                phone_number = order_one[0]['created_by']['phone_number']
                aknel_gel = order_one[0]['aknel_gel']
                data['aknel_gel'] = aknel_gel
                astarakson_1125 = order_one[0]['astarakson_1125']
                data['astarakson_1125'] = astarakson_1125
                astarakson_562 = order_one[0]['astarakson_562']
                data['astarakson_562'] = astarakson_562
                astaryus = order_one[0]['astaryus']
                data['astaryus'] = astaryus
                intrizol = order_one[0]['intrizol']
                data['intrizol'] = intrizol
                livomed_tab = order_one[0]['livomed_tab']
                data['livomed_tab'] = livomed_tab
                livomed_sirop = order_one[0]['livomed_sirop']
                data['livomed_sirop'] = livomed_sirop
                renum_cap = order_one[0]['renum_cap']
                data['renum_cap'] = renum_cap
                stresson_cap = order_one[0]['stresson_cap']
                data['stresson_cap'] = stresson_cap
                tavamed = order_one[0]['tavamed']
                data['tavamed'] = tavamed
                x_payls_maz = order_one[0]['x_payls_maz']
                data['x_payls_maz'] = x_payls_maz
                seprazon = order_one[0]['seprazon']
                data['seprazon'] = seprazon
                entro_d_cap = order_one[0]['entro_d_cap']
                data['entro_d_cap'] = entro_d_cap
                entro_d_sashe = order_one[0]['entro_d_sashe']
                data['entro_d_sashe'] = entro_d_sashe
                lamino_100 = order_one[0]['lamino_100']
                data['lamino_100'] = lamino_100
                lamino_200 = order_one[0]['lamino_200']
                data['lamino_200'] = lamino_200
                text = f"<b>{translate(data['lang'], 'COMPANY_NAME')}:{company_name}\n{translate(data['lang'], 'INN_GET')}:{inn}\n{translate(data['lang'], 'CREATOR')}: {translate_cyrillic_or_latin(created_by, data['lang'])}</b>\n\n"
                product_list = []
                if aknel_gel != 0:
                    text += f'{translate_cyrillic_or_latin("Акнель гель 10гр", data["lang"])}: {aknel_gel}\n'
                    product_list.append({'name': 'Акнель гель 10гр', 'id': 'aknel_gel'})
                if astarakson_1125 != 0:
                    product_list.append({"name": 'Астароксон TZ-1125', 'id': 'astarakson_1125'})
                    text += f'{translate_cyrillic_or_latin("Астароксон TZ-1125", data["lang"])}: {astarakson_1125}\n'
                if astarakson_562 != 0:
                    product_list.append({'name': 'Астароксон TZ-562,5', 'id': 'astarakson_562'})
                    text += f"{translate_cyrillic_or_latin('Астароксон TZ-562,5 ', data['lang'])}: {astarakson_562}\n"
                if astaryus != 0:
                    product_list.append({'name': 'Астарюс 20мг/мл амп. 5мл №5', 'id': 'astaryus'})
                    text += f"{translate_cyrillic_or_latin('Астарюс 20мг/мл амп. 5мл №5 ', data['lang'])}: {astaryus}\n"
                if intrizol != 0:
                    product_list.append({'name': 'Интризол крем 20гр', 'id': 'intrizol'})
                    text += f"{translate_cyrillic_or_latin('Интризол крем 20гр', data['lang'])}: {intrizol}\n"
                if livomed_tab != 0:
                    product_list.append({'name': 'Ливомед таб №60', 'id': 'livomed_tab'})
                    text += f"{translate_cyrillic_or_latin('Ливомед таб №60', data['lang'])}: {livomed_tab}\n"
                if livomed_sirop != 0:
                    product_list.append({'name': 'Ливомед сироп 200мл', 'id': 'livomed_sirop'})
                    text += f"{translate_cyrillic_or_latin('Ливомед сироп 200мл', data['lang'])}: {livomed_sirop}\n"
                if renum_cap != 0:
                    product_list.append({'name': 'Ренум капс. 250мг №60', 'id': "renum_cap"})
                    text += f"{translate_cyrillic_or_latin('Ренум капс. 250мг №60', data['lang'])}: {renum_cap}\n"
                if stresson_cap != 0:
                    product_list.append({'name': 'Стрессон капс №20', 'id': 'stresson_cap'})
                    text += f"{translate_cyrillic_or_latin('Стрессон капс №20', data['lang'])}:  {stresson_cap}\n"
                if tavamed != 0:
                    product_list.append({'name': 'ТАВАМЕД 500мг инфузия 100мл', 'id': 'tavamed'})
                    text += f"{translate_cyrillic_or_latin('ТАВАМЕД 500мг инфузия 100мл', data['lang'])}: {tavamed}\n"
                if x_payls_maz != 0:
                    product_list.append({'name': "Х-пайлс мазь 30г", 'id': "x_payls_maz"})
                    text += f"{translate_cyrillic_or_latin('Х-пайлс мазь 30г', data['lang'])} {x_payls_maz}\n"
                if seprazon != 0:
                    product_list.append({'name': 'Цепразон 1,5г', 'id': "seprazon"})
                    text += f"{translate_cyrillic_or_latin('Цепразон 1,5г', data['lang'])}: {seprazon}\n"
                if entro_d_cap != 0:
                    product_list.append({'name': "Энтро Д капс №10", 'id': "entro_d_cap"})
                    text += f"{translate_cyrillic_or_latin('Энтро Д капс №10 ', data['lang'])}: {entro_d_cap}\n"
                if entro_d_sashe != 0:
                    product_list.append({'name': "Энтро Д саше №10", 'id': "entro_d_sashe"})
                    text += f"{translate_cyrillic_or_latin('Энтро Д саше №10', data['lang'])}: {entro_d_sashe}\n"
                if lamino_100 != 0:
                    product_list.append({"name": "Ламино 100 мл", 'id': "lamino_100"})
                    text += f"{translate_cyrillic_or_latin('Ламино 100 мл', data['lang'])}: {lamino_100}\n"
                if lamino_200 != 0:
                    product_list.append({'name': "Ламино 200 мл", 'id': "lamino_200"})
                    text += f"{translate_cyrillic_or_latin('Ламино 200 мл ', data['lang'])}: {lamino_200}\n"
                text += f"\n{translate(data['lang'], 'CREATED_DATE')}:{str(order_one[0]['created_at'][:10]) + ' ' + order_one[0]['created_at'][11:16]}\n{translate(data['lang'], 'CREATE_PRODUCT_STATUS')} : {is_manager_send}\n"
                await ProductResidueManagerState.begin.set()
                await message.bot.send_message(text=text, chat_id=message.chat.id, parse_mode='HTML',
                                               reply_markup=product_reply_markup(data['lang'],
                                                                                 product_list=product_list))
            else:
                company = Company(company_id=data['company_id'], token=data['token']).get_one()
                company_name = company['company_name']
                inn = company['inn']
                # company_director_name = order_one[0]['company']['company_director_name']
                # company_director_phone_number = order_one[0]['company']['company_director_phone_number']
                # district = data['district']
                created_by = data['first_name']
                # if data['last_name']:
                #     created_by = f'{order_one[0]["created_by"]["first_name"]} {order_one[0]["created_by"]["last_name"]}'
                # phone_number = order_one[0]['created_by']['phone_number']
                aknel_gel = data['aknel_gel']
                astarakson_1125 = data['astarakson_1125']
                astarakson_562 = data['astarakson_562']
                astaryus = data['astaryus']
                intrizol = data['intrizol']
                livomed_tab = data['livomed_tab']
                livomed_sirop = data['livomed_sirop']
                renum_cap = data['renum_cap']
                stresson_cap = data['stresson_cap']
                tavamed = data['tavamed']
                x_payls_maz = data['x_payls_maz']
                seprazon = data['seprazon']
                entro_d_cap = data['entro_d_cap']
                entro_d_sashe = data['entro_d_sashe']
                lamino_100 = data['lamino_100']
                lamino_200 = data['lamino_200']
                text = f"<b>{translate(data['lang'], 'COMPANY_NAME')}:{company_name}\n{translate(data['lang'], 'INN_GET')}:{inn}\n{translate(data['lang'], 'CREATOR')}: {translate_cyrillic_or_latin(created_by, data['lang'])}</b>\n\n"
                product_list = []
                # if aknel_gel == 0:
                text += f'{translate_cyrillic_or_latin("Акнель гель 10гр", data["lang"])}: {aknel_gel}\n'
                product_list.append({'name': 'Акнель гель 10гр', 'id': 'aknel_gel'})
                # if astarakson_1125 != 0:
                product_list.append({"name": 'Астароксон TZ-1125', 'id': 'astarakson_1125'})
                text += f'{translate_cyrillic_or_latin("Астароксон TZ-1125", data["lang"])}: {astarakson_1125}\n'
                product_list.append({'name': 'Астароксон TZ-562,5', 'id': 'astarakson_562'})
                text += f"{translate_cyrillic_or_latin('Астароксон TZ-562,5 ', data['lang'])}: {astarakson_562}\n"
                product_list.append({'name': 'Астарюс 20мг/мл амп. 5мл №5', 'id': 'astaryus'})
                text += f"{translate_cyrillic_or_latin('Астарюс 20мг/мл амп. 5мл №5 ', data['lang'])}: {astaryus}\n"
                product_list.append({'name': 'Интризол крем 20гр', 'id': 'intrizol'})
                text += f"{translate_cyrillic_or_latin('Интризол крем 20гр', data['lang'])}: {intrizol}\n"
                product_list.append({'name': 'Ливомед таб №60', 'id': 'livomed_tab'})
                text += f"{translate_cyrillic_or_latin('Ливомед таб №60', data['lang'])}: {livomed_tab}\n"
                product_list.append({'name': 'Ливомед сироп 200мл', 'id': 'livomed_sirop'})
                text += f"{translate_cyrillic_or_latin('Ливомед сироп 200мл', data['lang'])}: {livomed_sirop}\n"
                product_list.append({'name': 'Ренум капс. 250мг №60', 'id': "renum_cap"})
                text += f"{translate_cyrillic_or_latin('Ренум капс. 250мг №60', data['lang'])}: {renum_cap}\n"
                product_list.append({'name': 'Стрессон капс №20', 'id': 'stresson_cap'})
                text += f"{translate_cyrillic_or_latin('Стрессон капс №20', data['lang'])}:  {stresson_cap}\n"
                product_list.append({'name': 'ТАВАМЕД 500мг инфузия 100мл', 'id': 'tavamed'})
                text += f"{translate_cyrillic_or_latin('ТАВАМЕД 500мг инфузия 100мл', data['lang'])}: {tavamed}\n"
                product_list.append({'name': "Х-пайлс мазь 30г", 'id': "x_payls_maz"})
                text += f"{translate_cyrillic_or_latin('Х-пайлс мазь 30г', data['lang'])} {x_payls_maz}\n"
                product_list.append({'name': 'Цепразон 1,5г', 'id': "seprazon"})
                text += f"{translate_cyrillic_or_latin('Цепразон 1,5г', data['lang'])}: {seprazon}\n"
                product_list.append({'name': "Энтро Д капс №10", 'id': "entro_d_cap"})
                text += f"{translate_cyrillic_or_latin('Энтро Д капс №10 ', data['lang'])}: {entro_d_cap}\n"
                product_list.append({'name': "Энтро Д саше №10", 'id': "entro_d_sashe"})
                text += f"{translate_cyrillic_or_latin('Энтро Д саше №10', data['lang'])}: {entro_d_sashe}\n"
                product_list.append({"name": "Ламино 100 мл", 'id': "lamino_100"})
                text += f"{translate_cyrillic_or_latin('Ламино 100 мл', data['lang'])}: {lamino_100}\n"
                product_list.append({'name': "Ламино 200 мл", 'id': "lamino_200"})
                text += f"{translate_cyrillic_or_latin('Ламино 200 мл ', data['lang'])}: {lamino_200}\n"
                text += f"\n"
                await ProductResidueManagerState.begin.set()
                await message.bot.send_message(text=text, chat_id=message.chat.id, parse_mode='HTML',
                                               reply_markup=product_reply_markup(data['lang'],
                                                                                 product_list=product_list))
            return
        text = translate(data['lang'], 'BACK')
        await BaseState.base.set()
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.message_handler(
    lambda message: (str(message.text).__eq__(latin['BACK_MENU']) or str(message.text).__eq__(
        russian['BACK_MENU']) or str(
        message.text).__eq__(translate_cyrillic_or_latin(latin['BACK_MENU'], 'cyr'))) and (
                            not str(message.text).__eq__('/start')),
    state=[ProductResidueManagerState.reply_product])
async def back_menu_base_menu_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        text = translate(data['lang'], 'CHOICE_COUNT_UPDATE')
        await ProductResidueManagerState.new_product.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id)


@dp.callback_query_handler(state=ProductResidueManagerState.reply_product)
async def cal_back_reply_product_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        order_one = HospitalResidue(company=data['order_id'], token=data['token']).hospital_user_vizit()
        if order_one:
            data['order'] = order_one[0]['id']
            data['checked'] = 'yes'
        else:
            data['checked'] = 'no'
        if call.data.__eq__('yes'):
            order_one = HospitalResidue(company=data['order_id'], token=data['token']).hospital_user_vizit()
            if order_one:
                is_manager_send = ""
                if order_one[0]['status'].__eq__('office_manager'):
                    is_manager_send = translate_cyrillic_or_latin("Offis Menedjerda", data['lang'])
                elif order_one[0]['status'].__eq__('delivery'):
                    is_manager_send = translate_cyrillic_or_latin("Omborxonada", data['lang'])
                elif order_one[0]['status'].__eq__('supplier'):
                    is_manager_send = translate_cyrillic_or_latin("Yetkazib beruvchida", data['lang'])
                if order_one[0]['status'] is None:
                    is_manager_send = translate_cyrillic_or_latin('MP/Menedjerda', data['lang'])
                company_name = order_one[0]['company']['company_name']
                inn = order_one[0]['company']['inn']
                company_director_name = order_one[0]['company']['company_director_name']
                company_director_phone_number = order_one[0]['company']['company_director_phone_number']
                district = order_one[0]['district']['name']
                created_by = order_one[0]["created_by"]['first_name']
                if order_one[0]["created_by"]['last_name']:
                    created_by = f'{order_one[0]["created_by"]["first_name"]} {order_one[0]["created_by"]["last_name"]}'
                phone_number = order_one[0]['created_by']['phone_number']
                aknel_gel = data['aknel_gel']
                astarakson_1125 = data['astarakson_1125']
                astarakson_562 = data['astarakson_562']
                astaryus = data['astaryus']
                intrizol = data['intrizol']
                livomed_tab = data['livomed_tab']
                livomed_sirop = data['livomed_sirop']
                renum_cap = data['renum_cap']
                stresson_cap = data['stresson_cap']
                tavamed = data['tavamed']
                x_payls_maz = data['x_payls_maz']
                seprazon = data['seprazon']
                entro_d_cap = data['entro_d_cap']
                entro_d_sashe = data['entro_d_sashe']
                lamino_100 = data['lamino_100']
                lamino_200 = data['lamino_200']
                text = f"<b>{translate(data['lang'], 'COMPANY_NAME')}:{company_name}\n{translate(data['lang'], 'INN_GET')}:{inn}\n{translate(data['lang'], 'CREATOR')}: {translate_cyrillic_or_latin(created_by, data['lang'])}</b>\n\n"
                product_list = []
                if aknel_gel != 0:
                    text += f'{translate_cyrillic_or_latin("Акнель гель 10гр", data["lang"])}: {aknel_gel}\n'
                    product_list.append({'name': 'Акнель гель 10гр', 'id': 'aknel_gel'})
                if astarakson_1125 != 0:
                    product_list.append({"name": 'Астароксон TZ-1125', 'id': 'astarakson_1125'})
                    text += f'{translate_cyrillic_or_latin("Астароксон TZ-1125", data["lang"])}: {astarakson_1125}\n'
                if astarakson_562 != 0:
                    product_list.append({'name': 'Астароксон TZ-562,5', 'id': 'astarakson_562'})
                    text += f"{translate_cyrillic_or_latin('Астароксон TZ-562,5 ', data['lang'])}: {astarakson_562}\n"
                if astaryus != 0:
                    product_list.append({'name': 'Астарюс 20мг/мл амп. 5мл №5', 'id': 'astaryus'})
                    text += f"{translate_cyrillic_or_latin('Астарюс 20мг/мл амп. 5мл №5 ', data['lang'])}: {astaryus}\n"
                if intrizol != 0:
                    product_list.append({'name': 'Интризол крем 20гр', 'id': 'intrizol'})
                    text += f"{translate_cyrillic_or_latin('Интризол крем 20гр', data['lang'])}: {intrizol}\n"
                if livomed_tab != 0:
                    product_list.append({'name': 'Ливомед таб №60', 'id': 'livomed_tab'})
                    text += f"{translate_cyrillic_or_latin('Ливомед таб №60', data['lang'])}: {livomed_tab}\n"
                if livomed_sirop != 0:
                    product_list.append({'name': 'Ливомед сироп 200мл', 'id': 'livomed_sirop'})
                    text += f"{translate_cyrillic_or_latin('Ливомед сироп 200мл', data['lang'])}: {livomed_sirop}\n"
                if renum_cap != 0:
                    product_list.append({'name': 'Ренум капс. 250мг №60', 'id': "renum_cap"})
                    text += f"{translate_cyrillic_or_latin('Ренум капс. 250мг №60', data['lang'])}: {renum_cap}\n"
                if stresson_cap != 0:
                    product_list.append({'name': 'Стрессон капс №20', 'id': 'stresson_cap'})
                    text += f"{translate_cyrillic_or_latin('Стрессон капс №20', data['lang'])}:  {stresson_cap}\n"
                if tavamed != 0:
                    product_list.append({'name': 'ТАВАМЕД 500мг инфузия 100мл', 'id': 'tavamed'})
                    text += f"{translate_cyrillic_or_latin('ТАВАМЕД 500мг инфузия 100мл', data['lang'])}: {tavamed}\n"
                if x_payls_maz != 0:
                    product_list.append({'name': "Х-пайлс мазь 30г", 'id': "x_payls_maz"})
                    text += f"{translate_cyrillic_or_latin('Х-пайлс мазь 30г', data['lang'])} {x_payls_maz}\n"
                if seprazon != 0:
                    product_list.append({'name': 'Цепразон 1,5г', 'id': "seprazon"})
                    text += f"{translate_cyrillic_or_latin('Цепразон 1,5г', data['lang'])}: {seprazon}\n"
                if entro_d_cap != 0:
                    product_list.append({'name': "Энтро Д капс №10", 'id': "entro_d_cap"})
                    text += f"{translate_cyrillic_or_latin('Энтро Д капс №10 ', data['lang'])}: {entro_d_cap}\n"
                if entro_d_sashe != 0:
                    product_list.append({'name': "Энтро Д саше №10", 'id': "entro_d_sashe"})
                    text += f"{translate_cyrillic_or_latin('Энтро Д саше №10', data['lang'])}: {entro_d_sashe}\n"
                if lamino_100 != 0:
                    product_list.append({"name": "Ламино 100 мл", 'id': "lamino_100"})
                    text += f"{translate_cyrillic_or_latin('Ламино 100 мл', data['lang'])}: {lamino_100}\n"
                if lamino_200 != 0:
                    product_list.append({'name': "Ламино 200 мл", 'id': "lamino_200"})
                    text += f"{translate_cyrillic_or_latin('Ламино 200 мл ', data['lang'])}: {lamino_200}\n"
                text += f"\n{translate(data['lang'], 'CREATED_DATE')}:{str(order_one[0]['created_at'][:10]) + ' ' + order_one[0]['created_at'][11:16]}\n{translate(data['lang'], 'CREATE_PRODUCT_STATUS')} : {is_manager_send}\n"
                await ProductResidueManagerState.new_begin.set()
                await call.message.bot.send_message(text=text, chat_id=call.message.chat.id, parse_mode='HTML',
                                                    reply_markup=product_reply_markup(data['lang'],
                                                                                      product_list=product_list))
            else:
                company = Company(company_id=data['company_id'], token=data['token']).get_one()
                company_name = company['company_name']
                inn = company['inn']
                created_by = data['first_name']
                aknel_gel = data['aknel_gel']
                astarakson_1125 = data['astarakson_1125']
                astarakson_562 = data['astarakson_562']
                astaryus = data['astaryus']
                intrizol = data['intrizol']
                livomed_tab = data['livomed_tab']
                livomed_sirop = data['livomed_sirop']
                renum_cap = data['renum_cap']
                stresson_cap = data['stresson_cap']
                tavamed = data['tavamed']
                x_payls_maz = data['x_payls_maz']
                seprazon = data['seprazon']
                entro_d_cap = data['entro_d_cap']
                entro_d_sashe = data['entro_d_sashe']
                lamino_100 = data['lamino_100']
                lamino_200 = data['lamino_200']
                text = f"<b>{translate(data['lang'], 'COMPANY_NAME')}:{company_name}\n{translate(data['lang'], 'INN_GET')}:{inn}\n{translate(data['lang'], 'CREATOR')}: {translate_cyrillic_or_latin(created_by, data['lang'])}</b>\n\n"
                product_list = []
                # if aknel_gel == 0:
                text += f'{translate_cyrillic_or_latin("Акнель гель 10гр", data["lang"])}: {aknel_gel}\n'
                product_list.append({'name': 'Акнель гель 10гр', 'id': 'aknel_gel'})
                # if astarakson_1125 != 0:
                product_list.append({"name": 'Астароксон TZ-1125', 'id': 'astarakson_1125'})
                text += f'{translate_cyrillic_or_latin("Астароксон TZ-1125", data["lang"])}: {astarakson_1125}\n'
                product_list.append({'name': 'Астароксон TZ-562,5', 'id': 'astarakson_562'})
                text += f"{translate_cyrillic_or_latin('Астароксон TZ-562,5 ', data['lang'])}: {astarakson_562}\n"
                product_list.append({'name': 'Астарюс 20мг/мл амп. 5мл №5', 'id': 'astaryus'})
                text += f"{translate_cyrillic_or_latin('Астарюс 20мг/мл амп. 5мл №5 ', data['lang'])}: {astaryus}\n"
                product_list.append({'name': 'Интризол крем 20гр', 'id': 'intrizol'})
                text += f"{translate_cyrillic_or_latin('Интризол крем 20гр', data['lang'])}: {intrizol}\n"
                product_list.append({'name': 'Ливомед таб №60', 'id': 'livomed_tab'})
                text += f"{translate_cyrillic_or_latin('Ливомед таб №60', data['lang'])}: {livomed_tab}\n"
                product_list.append({'name': 'Ливомед сироп 200мл', 'id': 'livomed_sirop'})
                text += f"{translate_cyrillic_or_latin('Ливомед сироп 200мл', data['lang'])}: {livomed_sirop}\n"
                product_list.append({'name': 'Ренум капс. 250мг №60', 'id': "renum_cap"})
                text += f"{translate_cyrillic_or_latin('Ренум капс. 250мг №60', data['lang'])}: {renum_cap}\n"
                product_list.append({'name': 'Стрессон капс №20', 'id': 'stresson_cap'})
                text += f"{translate_cyrillic_or_latin('Стрессон капс №20', data['lang'])}:  {stresson_cap}\n"
                product_list.append({'name': 'ТАВАМЕД 500мг инфузия 100мл', 'id': 'tavamed'})
                text += f"{translate_cyrillic_or_latin('ТАВАМЕД 500мг инфузия 100мл', data['lang'])}: {tavamed}\n"
                product_list.append({'name': "Х-пайлс мазь 30г", 'id': "x_payls_maz"})
                text += f"{translate_cyrillic_or_latin('Х-пайлс мазь 30г', data['lang'])} {x_payls_maz}\n"
                product_list.append({'name': 'Цепразон 1,5г', 'id': "seprazon"})
                text += f"{translate_cyrillic_or_latin('Цепразон 1,5г', data['lang'])}: {seprazon}\n"
                product_list.append({'name': "Энтро Д капс №10", 'id': "entro_d_cap"})
                text += f"{translate_cyrillic_or_latin('Энтро Д капс №10 ', data['lang'])}: {entro_d_cap}\n"
                product_list.append({'name': "Энтро Д саше №10", 'id': "entro_d_sashe"})
                text += f"{translate_cyrillic_or_latin('Энтро Д саше №10', data['lang'])}: {entro_d_sashe}\n"
                product_list.append({"name": "Ламино 100 мл", 'id': "lamino_100"})
                text += f"{translate_cyrillic_or_latin('Ламино 100 мл', data['lang'])}: {lamino_100}\n"
                product_list.append({'name': "Ламино 200 мл", 'id': "lamino_200"})
                text += f"{translate_cyrillic_or_latin('Ламино 200 мл ', data['lang'])}: {lamino_200}\n"
                text += f"\n"
                await ProductResidueManagerState.new_begin.set()
                await call.message.bot.send_message(text=text, chat_id=call.message.chat.id, parse_mode='HTML',
                                                    reply_markup=product_reply_markup(data['lang'],
                                                                                      product_list=product_list))
        else:
            if str(data['checked']).__eq__('yes'):
                user = get_one_user(data['user_id'])
                # text = translate(data['lang'], 'SUCCESS')
                company = Company(company_id=data['company_id'], token=data['token']).get_one()
                company_name = company['company_name']
                inn = company['inn']
                aknel_gel = data['aknel_gel']
                astarakson_1125 = data['astarakson_1125']
                astarakson_562 = data['astarakson_562']
                astaryus = data['astaryus']
                intrizol = data['intrizol']
                livomed_tab = data['livomed_tab']
                livomed_sirop = data['livomed_sirop']
                renum_cap = data['renum_cap']
                stresson_cap = data['stresson_cap']
                tavamed = data['tavamed']
                x_payls_maz = data['x_payls_maz']
                seprazon = data['seprazon']
                entro_d_cap = data['entro_d_cap']
                entro_d_sashe = data['entro_d_sashe']
                lamino_100 = data['lamino_100']
                lamino_200 = data['lamino_200']
                created_by = data['first_name']
                text = f"<b>{translate(data['lang'], 'COMPANY_NAME')}:{company_name}\n{translate(data['lang'], 'INN_GET')}:{inn}\n{translate(data['lang'], 'CREATOR')}: {translate_cyrillic_or_latin(created_by, data['lang'])}</b>\n\n"
                product_list = []
                text += f'{translate_cyrillic_or_latin("Акнель гель 10гр", data["lang"])}: {aknel_gel}\n'
                product_list.append({'name': 'Акнель гель 10гр', 'id': 'aknel_gel'})
                product_list.append({"name": 'Астароксон TZ-1125', 'id': 'astarakson_1125'})
                text += f'{translate_cyrillic_or_latin("Астароксон TZ-1125", data["lang"])}: {astarakson_1125}\n'
                product_list.append({'name': 'Астароксон TZ-562,5', 'id': 'astarakson_562'})
                text += f"{translate_cyrillic_or_latin('Астароксон TZ-562,5 ', data['lang'])}: {astarakson_562}\n"
                product_list.append({'name': 'Астарюс 20мг/мл амп. 5мл №5', 'id': 'astaryus'})
                text += f"{translate_cyrillic_or_latin('Астарюс 20мг/мл амп. 5мл №5 ', data['lang'])}: {astaryus}\n"
                product_list.append({'name': 'Интризол крем 20гр', 'id': 'intrizol'})
                text += f"{translate_cyrillic_or_latin('Интризол крем 20гр', data['lang'])}: {intrizol}\n"
                product_list.append({'name': 'Ливомед таб №60', 'id': 'livomed_tab'})
                text += f"{translate_cyrillic_or_latin('Ливомед таб №60', data['lang'])}: {livomed_tab}\n"
                product_list.append({'name': 'Ливомед сироп 200мл', 'id': 'livomed_sirop'})
                text += f"{translate_cyrillic_or_latin('Ливомед сироп 200мл', data['lang'])}: {livomed_sirop}\n"
                product_list.append({'name': 'Ренум капс. 250мг №60', 'id': "renum_cap"})
                text += f"{translate_cyrillic_or_latin('Ренум капс. 250мг №60', data['lang'])}: {renum_cap}\n"
                product_list.append({'name': 'Стрессон капс №20', 'id': 'stresson_cap'})
                text += f"{translate_cyrillic_or_latin('Стрессон капс №20', data['lang'])}:  {stresson_cap}\n"
                product_list.append({'name': 'ТАВАМЕД 500мг инфузия 100мл', 'id': 'tavamed'})
                text += f"{translate_cyrillic_or_latin('ТАВАМЕД 500мг инфузия 100мл', data['lang'])}: {tavamed}\n"
                product_list.append({'name': "Х-пайлс мазь 30г", 'id': "x_payls_maz"})
                text += f"{translate_cyrillic_or_latin('Х-пайлс мазь 30г', data['lang'])} {x_payls_maz}\n"
                product_list.append({'name': 'Цепразон 1,5г', 'id': "seprazon"})
                text += f"{translate_cyrillic_or_latin('Цепразон 1,5г', data['lang'])}: {seprazon}\n"
                product_list.append({'name': "Энтро Д капс №10", 'id': "entro_d_cap"})
                text += f"{translate_cyrillic_or_latin('Энтро Д капс №10 ', data['lang'])}: {entro_d_cap}\n"
                product_list.append({'name': "Энтро Д саше №10", 'id': "entro_d_sashe"})
                text += f"{translate_cyrillic_or_latin('Энтро Д саше №10', data['lang'])}: {entro_d_sashe}\n"
                product_list.append({"name": "Ламино 100 мл", 'id': "lamino_100"})
                text += f"{translate_cyrillic_or_latin('Ламино 100 мл', data['lang'])}: {lamino_100}\n"
                product_list.append({'name': "Ламино 200 мл", 'id': "lamino_200"})
                text += f"{translate_cyrillic_or_latin('Ламино 200 мл ', data['lang'])}: {lamino_200}\n"
                text += f"\n"
                HospitalResidue(created_by=data['user_id'],
                                district=user['district'],
                                status='office_manager',
                                company=data['company_id'],
                                order_id=data['order'],
                                aknel_gel=data['aknel_gel'], astarakson_1125=data['astarakson_1125'],
                                astarakson_562=data['astarakson_562'], astaryus=data['astaryus'],
                                intrizol=data['intrizol'],
                                livomed_tab=data['livomed_tab'], livomed_sirop=data['livomed_sirop'],
                                renum_cap=data['renum_cap'], stresson_cap=data['stresson_cap'], tavamed=data['tavamed'],
                                x_plays_maz=data['x_payls_maz'], seprazon=data['seprazon'],
                                entro_d_cap=data['entro_d_cap'],
                                entro_d_sashe=data['entro_d_sashe'], lamino_100=data['lamino_100'],
                                lamino_200=data['lamino_200'], token=data['token']).update()
                await BaseState.base.set()
                await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                    reply_markup=base_menu(data['lang'], data['role']))
            else:
                user = get_one_user(data['user_id'])
                # text = translate(data['lang'], 'SUCCESS')
                company = Company(company_id=data['company_id'], token=data['token']).get_one()
                company_name = company['company_name']
                inn = company['inn']
                aknel_gel = data['aknel_gel']
                astarakson_1125 = data['astarakson_1125']
                astarakson_562 = data['astarakson_562']
                astaryus = data['astaryus']
                intrizol = data['intrizol']
                livomed_tab = data['livomed_tab']
                livomed_sirop = data['livomed_sirop']
                renum_cap = data['renum_cap']
                stresson_cap = data['stresson_cap']
                tavamed = data['tavamed']
                x_payls_maz = data['x_payls_maz']
                seprazon = data['seprazon']
                entro_d_cap = data['entro_d_cap']
                entro_d_sashe = data['entro_d_sashe']
                lamino_100 = data['lamino_100']
                lamino_200 = data['lamino_200']
                created_by = data['first_name']
                text = f"<b>{translate(data['lang'], 'COMPANY_NAME')}:{company_name}\n{translate(data['lang'], 'INN_GET')}:{inn}\n{translate(data['lang'], 'CREATOR')}: {translate_cyrillic_or_latin(created_by, data['lang'])}</b>\n\n"
                product_list = []
                text += f'{translate_cyrillic_or_latin("Акнель гель 10гр", data["lang"])}: {aknel_gel}\n'
                product_list.append({'name': 'Акнель гель 10гр', 'id': 'aknel_gel'})
                product_list.append({"name": 'Астароксон TZ-1125', 'id': 'astarakson_1125'})
                text += f'{translate_cyrillic_or_latin("Астароксон TZ-1125", data["lang"])}: {astarakson_1125}\n'
                product_list.append({'name': 'Астароксон TZ-562,5', 'id': 'astarakson_562'})
                text += f"{translate_cyrillic_or_latin('Астароксон TZ-562,5 ', data['lang'])}: {astarakson_562}\n"
                product_list.append({'name': 'Астарюс 20мг/мл амп. 5мл №5', 'id': 'astaryus'})
                text += f"{translate_cyrillic_or_latin('Астарюс 20мг/мл амп. 5мл №5 ', data['lang'])}: {astaryus}\n"
                product_list.append({'name': 'Интризол крем 20гр', 'id': 'intrizol'})
                text += f"{translate_cyrillic_or_latin('Интризол крем 20гр', data['lang'])}: {intrizol}\n"
                product_list.append({'name': 'Ливомед таб №60', 'id': 'livomed_tab'})
                text += f"{translate_cyrillic_or_latin('Ливомед таб №60', data['lang'])}: {livomed_tab}\n"
                product_list.append({'name': 'Ливомед сироп 200мл', 'id': 'livomed_sirop'})
                text += f"{translate_cyrillic_or_latin('Ливомед сироп 200мл', data['lang'])}: {livomed_sirop}\n"
                product_list.append({'name': 'Ренум капс. 250мг №60', 'id': "renum_cap"})
                text += f"{translate_cyrillic_or_latin('Ренум капс. 250мг №60', data['lang'])}: {renum_cap}\n"
                product_list.append({'name': 'Стрессон капс №20', 'id': 'stresson_cap'})
                text += f"{translate_cyrillic_or_latin('Стрессон капс №20', data['lang'])}:  {stresson_cap}\n"
                product_list.append({'name': 'ТАВАМЕД 500мг инфузия 100мл', 'id': 'tavamed'})
                text += f"{translate_cyrillic_or_latin('ТАВАМЕД 500мг инфузия 100мл', data['lang'])}: {tavamed}\n"
                product_list.append({'name': "Х-пайлс мазь 30г", 'id': "x_payls_maz"})
                text += f"{translate_cyrillic_or_latin('Х-пайлс мазь 30г', data['lang'])} {x_payls_maz}\n"
                product_list.append({'name': 'Цепразон 1,5г', 'id': "seprazon"})
                text += f"{translate_cyrillic_or_latin('Цепразон 1,5г', data['lang'])}: {seprazon}\n"
                product_list.append({'name': "Энтро Д капс №10", 'id': "entro_d_cap"})
                text += f"{translate_cyrillic_or_latin('Энтро Д капс №10 ', data['lang'])}: {entro_d_cap}\n"
                product_list.append({'name': "Энтро Д саше №10", 'id': "entro_d_sashe"})
                text += f"{translate_cyrillic_or_latin('Энтро Д саше №10', data['lang'])}: {entro_d_sashe}\n"
                product_list.append({"name": "Ламино 100 мл", 'id': "lamino_100"})
                text += f"{translate_cyrillic_or_latin('Ламино 100 мл', data['lang'])}: {lamino_100}\n"
                product_list.append({'name': "Ламино 200 мл", 'id': "lamino_200"})
                text += f"{translate_cyrillic_or_latin('Ламино 200 мл ', data['lang'])}: {lamino_200}\n"
                text += f"\n"
                user = get_one_user(data['user_id'])
                text = translate(data['lang'], 'SUCCESS')
                HospitalResidue(created_by=data['user_id'],
                                district=user['district'],
                                status='office_manager',
                                company=data['company_id'],
                                aknel_gel=data['aknel_gel'], astarakson_1125=data['astarakson_1125'],
                                astarakson_562=data['astarakson_562'], astaryus=data['astaryus'],
                                intrizol=data['intrizol'],
                                livomed_tab=data['livomed_tab'], livomed_sirop=data['livomed_sirop'],
                                renum_cap=data['renum_cap'], stresson_cap=data['stresson_cap'], tavamed=data['tavamed'],
                                x_plays_maz=data['x_payls_maz'], seprazon=data['seprazon'],
                                entro_d_cap=data['entro_d_cap'],
                                entro_d_sashe=data['entro_d_sashe'], lamino_100=data['lamino_100'],
                                lamino_200=data['lamino_200'], token=data['token']).create()
                await BaseState.base.set()
                await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                    reply_markup=base_menu(data['lang'], data['role']))


@dp.callback_query_handler(state=ProductResidueManagerState.new_begin)
async def call_back_product_choice_handler(call: types.CallbackQuery, state: FSMContext):
    props = call.data
    async with state.proxy() as data:
        data['product_pharmacy'] = props
        if props.__eq__('back'):
            text = translate(data['lang'], 'BACK')
            await HospitalResidueManagerState.begin.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=company_all_inline(data['page'], data['search'],
                                                                                data['token'],
                                                                                data['lang']))
        else:
            text = translate(data['lang'], 'CHOICE_COUNT_UPDATE')
            await ProductResidueManagerState.new_products.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id)


@dp.message_handler(state=ProductResidueManagerState.new_products)
async def pharmacy_residue_new_product_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            int(message.text)
        except:
            text = translate(data['lang'], 'BAD_REQUEST')
            await message.bot.send_message(text=text, chat_id=message.chat.id)
        props = data['product_pharmacy']
        if props.__eq__('aknel_gel'):
            data['aknel_gel'] = message.text
        if props.__eq__('astarakson_1125'):
            data['astarakson_1125'] = message.text
        if props.__eq__('astarakson_562'):
            data['astarakson_562'] = message.text
        if props.__eq__("astaryus"):
            data['astaryus'] = message.text
        if props.__eq__('intrizol'):
            data['intrizol'] = message.text
        if props.__eq__('livomed_tab'):
            data['livomed_tab'] = message.text
        if props.__eq__('livomed_sirop'):
            data['livomed_sirop'] = message.text
        if props.__eq__('renum_cap'):
            data['renum_cap'] = message.text
        if props.__eq__('stresson_cap'):
            data['stresson_cap'] = message.text
        if props.__eq__('tavamed'):
            data['tavamed'] = message.text
        if props.__eq__('x_payls_maz'):
            data['x_payls_maz'] = message.text
        if props.__eq__('seprazon'):
            data['seprazon'] = message.text
        if props.__eq__('entro_d_cap'):
            data['entro_d_cap'] = message.text
        if props.__eq__('entro_d_sashe'):
            data['entro_d_sashe'] = message.text
        if props.__eq__('lamino_100'):
            data['lamino_100'] = message.text
        if props.__eq__('lamino_200'):
            data['lamino_200'] = message.text
        text = translate(data['lang'], 'CHOICE_REPLY')
        await ProductResidueManagerState.reply_product.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id, reply_markup=check_basket(data['lang']))
