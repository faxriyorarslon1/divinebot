from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate_cyrillic_or_latin, translate
from Tranlate.translate_language import latin, russian
from api.orders.debit import Debit
from api.users import district_retrieve
from api.users.users import get_one_user
from button.inline import call_debit
from button.reply_markup import base_menu
from dispatch import dp
from excel_utils.order import get_excel_income, get_excel_debit
from states import BaseState, DebitState
from utils.number_split_for_price import price_split


@dp.message_handler(lambda message: (message.text.__eq__(russian['QARZDORLIK_AGENT']) or message.text.__eq__(
    latin['QARZDORLIK_AGENT']) or message.text.__eq__(
    translate_cyrillic_or_latin(latin['QARZDORLIK_AGENT'], 'cyr'))) and (not str(message.text).__eq__('/start')),
                    state=BaseState.base)
async def agent_debit_menu(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        get_excel_debit_file_name = Debit(token=data['token']).get_excel()
        data['page'] = 1
        if get_excel_debit_file_name:
            user = get_one_user(data['user_id'])
            district = district_retrieve(user['district'])
            name = user['first_name']
            if user['last_name']:
                name = f"{user['first_name']} {user['last_name']}"
            file = get_excel_debit(get_excel_debit_file_name['file_name'], all_name=name, village=district['name'])
            data['file'] = file
            text = ""
            total_price = 0
            if len(file) != 0:
                for i, f in enumerate(file[:(data['page'] * 20)], start=1):
                    total_price += float(f['price'])
                    text += f"{i})  {translate(data['lang'], 'NAME_MEMBER')}: {translate_cyrillic_or_latin(f['all_name'], data['lang'])}" \
                            f"\n{translate_cyrillic_or_latin('Dorixona Nomi(Korxona Nomi)', data['lang'])}:  {translate_cyrillic_or_latin(f['company_name'], data['lang'])}" \
                            f"\n{translate_cyrillic_or_latin('Olingan muddat', data['lang'])}: {str(f['received_period'])[:10]}" \
                            f"\n{translate_cyrillic_or_latin('Tegash Muddati', data['lang'])}: {str(f['deadline'])[0:10]}" \
                            f"\n{translate_cyrillic_or_latin('Kuni', data['lang'])}: {f['day']}" \
                            f"\n{translate_cyrillic_or_latin('Status', data['lang'])}: {f['status']}" \
                            f"\n{translate_cyrillic_or_latin('Qarzdorlik summasi', data['lang'])}: {price_split(f['price'])} {translate(data['lang'], 'SUM')}\n\n"
                text += f"{translate(data['lang'], 'TOTAL_PRICE')}:{price_split(total_price)} {translate(data['lang'], 'SUM')}"
                user = get_one_user(data['user_id'])
                data['role'] = user['role']
                datas = call_debit(data['page'], file, data['lang'])
                if datas:
                    await message.bot.send_message(text=text, chat_id=message.chat.id,
                                                   reply_markup=datas)
                    await DebitState.base.set()
                    return
                await message.bot.send_message(text=text, chat_id=message.chat.id,
                                               reply_markup=base_menu(data['lang'], data['role']))
                await BaseState.base.set()
                return
            text = translate(data['lang'], "NOT_FOUND")
            user = get_one_user(data['user_id'])
            data['role'] = user['role']
            await BaseState.base.set()
            await message.bot.send_message(text=text, chat_id=message.chat.id,
                                           reply_markup=base_menu(data['lang'], data['role']))
            return
        text = translate(data['lang'], "NOT_FOUND")
        user = get_one_user(data['user_id'])
        data['role'] = user['role']
        await BaseState.base.set()
        await message.bot.send_message(text=text, chat_id=message.chat.id,
                                       reply_markup=base_menu(data['lang'], data['role']))


@dp.callback_query_handler(state=DebitState.base)
async def debit_handler(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data.__eq__('back'):
            text = translate(data['lang'], "THE_BACK")
            user = get_one_user(data['user_id'])
            data['role'] = user['role']
            await BaseState.base.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=base_menu(data['lang'], data['role']))
        if call.data.__eq__('prev'):
            data['page'] -= 1
            total_price = 0
            text = ""
            if data['page'] == 1:
                for i, f in enumerate(data['file'][:(data['page'] * 20)], start=1):
                    total_price += float(f['price'])
                    text += f"{i})  {translate(data['lang'], 'NAME_MEMBER')}: {translate_cyrillic_or_latin(f['all_name'], data['lang'])}" \
                            f"\n{translate_cyrillic_or_latin('Dorixona Nomi(Korxona Nomi)', data['lang'])}:  {translate_cyrillic_or_latin(f['company_name'], data['lang'])}" \
                            f"\n{translate_cyrillic_or_latin('Olingan muddat', data['lang'])}: {str(f['received_period'])[:10]}" \
                            f"\n{translate_cyrillic_or_latin('Tegash Muddati', data['lang'])}: {str(f['deadline'])[0:10]}" \
                            f"\n{translate_cyrillic_or_latin('Kuni', data['lang'])}: {f['day']}" \
                            f"\n{translate_cyrillic_or_latin('Status', data['lang'])}: {f['status']}" \
                            f"\n{translate_cyrillic_or_latin('Qarzdorlik summasi', data['lang'])}: {price_split(f['price'])} {translate(data['lang'], 'SUM')}\n\n"
                text += f"{translate(data['lang'], 'TOTAL_PRICE')}:{price_split(total_price)} {translate(data['lang'], 'SUM')}"
                user = get_one_user(data['user_id'])
                data['role'] = user['role']
                datas = call_debit(data['page'], data['file'], data['lang'])
                if datas:
                    await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                        reply_markup=datas)
                    await DebitState.base.set()
                    return
                await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                    reply_markup=base_menu(data['lang'], data['role']))
                await BaseState.base.set()
                return
            for i, f in enumerate(data['file'][((data['page'] - 1) * 20):(data['page'] * 20)], start=1):
                total_price += float(f['price'])
                text += f"{i})  {translate(data['lang'], 'NAME_MEMBER')}: {translate_cyrillic_or_latin(f['all_name'], data['lang'])}" \
                        f"\n{translate_cyrillic_or_latin('Dorixona Nomi(Korxona Nomi)', data['lang'])}:  {translate_cyrillic_or_latin(f['company_name'], data['lang'])}" \
                        f"\n{translate_cyrillic_or_latin('Olingan muddat', data['lang'])}: {str(f['received_period'])[:10]}" \
                        f"\n{translate_cyrillic_or_latin('Tegash Muddati', data['lang'])}: {str(f['deadline'])[0:10]}" \
                        f"\n{translate_cyrillic_or_latin('Kuni', data['lang'])}: {f['day']}" \
                        f"\n{translate_cyrillic_or_latin('Status', data['lang'])}: {f['status']}" \
                        f"\n{translate_cyrillic_or_latin('Qarzdorlik summasi', data['lang'])}: {price_split(f['price'])} {translate(data['lang'], 'SUM')}\n\n"
            text += f"{translate(data['lang'], 'TOTAL_PRICE')}:{price_split(total_price)} {translate(data['lang'], 'SUM')}"
            user = get_one_user(data['user_id'])
            data['role'] = user['role']
            datas = call_debit(data['page'], data['file'], data['lang'])
            if datas:
                await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                    reply_markup=datas)
                await DebitState.base.set()
                return
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=base_menu(data['lang'], data['role']))
            await BaseState.base.set()
            return
        if call.data.__eq__('next'):
            data['page'] += 1
            total_price = 0
            text = ""
            for i, f in enumerate(data['file'][((data['page'] - 1) * 20):(data['page'] * 20)], start=1):
                total_price += float(f['price'])
                text += f"{i})  {translate(data['lang'], 'NAME_MEMBER')}: {translate_cyrillic_or_latin(f['all_name'], data['lang'])}" \
                        f"\n{translate_cyrillic_or_latin('Dorixona Nomi(Korxona Nomi)', data['lang'])}:  {translate_cyrillic_or_latin(f['company_name'], data['lang'])}" \
                        f"\n{translate_cyrillic_or_latin('Olingan muddat', data['lang'])}: {str(f['received_period'])[:10]}" \
                        f"\n{translate_cyrillic_or_latin('Tegash Muddati', data['lang'])}: {str(f['deadline'])[0:10]}" \
                        f"\n{translate_cyrillic_or_latin('Kuni', data['lang'])}: {f['day']}" \
                        f"\n{translate_cyrillic_or_latin('Status', data['lang'])}: {f['status']}" \
                        f"\n{translate_cyrillic_or_latin('Qarzdorlik summasi', data['lang'])}: {price_split(f['price'])} {translate(data['lang'], 'SUM')}\n\n"
            text += f"{translate(data['lang'], 'TOTAL_PRICE')}:{price_split(total_price)} {translate(data['lang'], 'SUM')}"
            user = get_one_user(data['user_id'])
            data['role'] = user['role']
            datas = call_debit(data['page'], data['file'], data['lang'])
            if datas:
                await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                    reply_markup=datas)
                await DebitState.base.set()
                return
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=base_menu(data['lang'], data['role']))
            await BaseState.base.set()
            return
