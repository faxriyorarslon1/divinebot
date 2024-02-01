from aiogram import types
from aiogram.dispatcher import FSMContext

from Tranlate.tranlate_config import translate
from api.product import delete_product
from api.users.users import get_one_user
from button.inline import office_manager_all_product_inline
from button.reply_markup import base_menu, crud_for_office_manager
from dispatch import dp
from states import BaseState
from states.orders import GetAllProductState, OrdersState


@dp.callback_query_handler(state=GetAllProductState.delete)
async def delete_for_product(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data.__eq__('yes'):
            text = translate(data['lang'], 'SUCCESS_DELETED')
            delete_product(product_id=data['product'], token=data['token'])
            await GetAllProductState.get_all.set()
            if office_manager_all_product_inline(data['page_office_manager'],
                                                 token=data['token']):
                await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                    reply_markup=office_manager_all_product_inline(
                                                        data['page_office_manager'],
                                                        token=data['token'], lang=data['lang']))
            else:
                text = translate(data['lang'], 'THE_BACK')
                await OrdersState.begin.set()
                await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                    reply_markup=crud_for_office_manager(data['lang']))
        else:
            text = translate(data['lang'], 'NO_SUCCESS')
            await GetAllProductState.get_all.set()
            await call.message.bot.send_message(text=text, chat_id=call.message.chat.id,
                                                reply_markup=office_manager_all_product_inline(
                                                    data['page_office_manager'],
                                                    token=data['token'], lang=data['lang']))
