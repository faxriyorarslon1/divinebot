import datetime

from aiogram.types import Message
from aiogram.utils.exceptions import ChatNotFound

import handlers
from aiogram.utils import executor, exceptions
from api.users import district_retrieve, district_get_all
from api.users.location import get_all_location_user
from api.users.users import get_agent, get_user_location, get_office_managers, get_agent_vizits
from configs.constants import BASE_URL
from dispatch import dp, bot
import asyncio
import aioschedule
from os.path import join as join_path

from excel_utils import check_excel
from excel_utils.order import get_excel_vizit
from excel_utils.user import USER_EXCEL_PATH, VIZIT_EXCEL_PATH

EXCEL_PATH = join_path(BASE_URL, 'excel_utils', 'excel', 'vizit')


async def send_admin():
    agents = get_agent()
    districts = district_get_all()
    for i in districts['results']:
        mp_managers = get_user_location(i['id'])
        text = ""
        for agent in agents:
            if len(mp_managers) != 0:
                text = f"Bugun ishga chiqmaganlar({i['name']})\n"
            for mp_manager in mp_managers:
                district = district_retrieve(mp_manager['district'])
                user = get_all_location_user(mp_manager['id'])
                if user['count'] == 0:
                    name = mp_manager['first_name']
                    if mp_manager['last_name']:
                        name = f"{mp_manager['first_name']} {mp_manager['last_name']}"
                    if mp_manager['role'] == "agent":
                        role = "Tibbiy Vakil"
                    else:
                        role = "Menedjer"
                    text += f"F.I.SH: {name}\nTelefon Raqami: {mp_manager['phone_number']}\nViloyati: {district['name']}\nLavozimi: {role}\n\n"
            if text:
                try:
                    message = Message(text=text)
                    text = message.html_text.split('\n')
                    lines = len(message.html_text.split('\n'))
                    first = 0
                    while first <= lines:
                        text2 = ''
                        if first + 80 < lines:
                            for m in text[first:first + 80]:
                                text2 += f"\n{m}"
                            await bot.send_message(chat_id=agent['chat_id'], text=text2)
                        else:
                            for m in text[first:lines]:
                                text2 += f"\n{m}"
                            await bot.send_message(chat_id=agent['chat_id'], text=text2)
                        first += 80
                except Exception:
                    print("Chat Not Found or blocked user")


async def send_admin2():
    office_managers = get_agent()
    districts = district_get_all()
    for i in districts['results']:
        excel_path = f'obshi_vizit_excel_{i["name"]}.xlsx'
        check_excel_params = check_excel(VIZIT_EXCEL_PATH, excel_path)
        for office in office_managers:
            if check_excel_params.__eq__("file yoq"):
                vizit = get_agent_vizits(district=i['id'])
                text = f"{i['name']} viloyati"
                if i['name'] == "Toshkent Shaxar":
                    text = f"{i['name']}"
                if i['name'] == "Toshkent Vil":
                    text = "Toshkent viloyati"
                for agent in vizit:
                    agent_name = agent['first_name']
                    if agent['last_name']:
                        agent_name += f"{agent['last_name']}"
                    text += f"\nIsmi: {agent['first_name']}\nViloyati:{i['name']}\nVizitlar Soni:0"
            else:
                vizit = get_agent_vizits(district=i['id'])
                text = f"{i['name']} viloyati"
                if i['name'] == "Toshkent Shaxar":
                    text = f"{i['name']}"
                if i['name'] == "Toshkent Vil":
                    text = "Toshkent viloyati"
                for agent in vizit:
                    agent_probel_name = agent['first_name']
                    agent_name = agent['first_name']
                    if agent['last_name']:
                        agent_name += f"{agent['last_name']}"
                        agent_probel_name += f" {agent['last_name']}"
                    name = get_excel_vizit(excel_path, agent_name, i['name'])
                    if name:
                        for n in name:
                            text += f"\nKim tomonidan: {n['all_name']}\nViloyat(Shaxar): {n['village']}\nKimga(Doctor ismi):{n['doctor_name']}\n" \
                                    f"Mutaxasisligi: {n['doctor_category']}\nTipi:{n['doctor_type']}\nTelefon Raqami: {n['doctor_phone']}\nIzoh: {n['comment']}\n"
                    else:
                        text += f"\nKim tomonidan: {agent_probel_name}\n"
                    text += f"Vizitlar Soni: {len(name)}\n"
            try:
                message = Message(text=text)
                text = message.html_text.split('\n')
                lines = len(message.html_text.split('\n'))
                first = 0
                while first <= lines:
                    text2 = ''
                    if first + 80 < lines:
                        for m in text[first:first + 80]:
                            text2 += f"\n{m}"
                        await bot.send_message(chat_id=office['chat_id'], text=text2)
                    else:
                        for m in text[first:lines]:
                            text2 += f"\n{m}"
                        await bot.send_message(chat_id=office['chat_id'], text=text2)
                    first += 80
            except Exception:
                print("Chat Not Found or blocked user")


async def scheduler():
    aioschedule.every().day.at("9:25").do(send_admin)
    aioschedule.every().day.at("19:00").do(send_admin2)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(10)


async def on_startup(_):
    asyncio.create_task(scheduler())
    # asyncio.create_task(scheduler2())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
