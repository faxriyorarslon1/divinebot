import json

import requests

from configs.constants import BASE_URL, BASE_API_URL


def district_order(district, day, month, token):
    url = f'{BASE_API_URL}/order/order/mp_agent_village/'
    reload = requests.get(url=url, params={"district": district, 'day': day, 'month': month},
                          headers={"Content-Type": "Application/json", "Authorization": f"Token {token}"}, verify=False)
    return json.loads(reload.text)


def worker_order(user_id, day, month, token):
    url = f'{BASE_API_URL}/order/order/mp_agent_order_office_manager/'
    reload = requests.get(url=url, params={"user": user_id, 'day': day, 'month': month},
                          headers={"Content-Type": 'Application/json', "Authorization": f"Token {token}"}, verify=False)
    return json.loads(reload.text)


def worker_mp_agent(role, district, token):
    url = f"{BASE_API_URL}/users/user/mp_agent_order/"
    reload = requests.get(url=url, params={"role": role, 'district': district},
                          headers={"Content-Type": "Application/json", "Authorization": f"Token {token}"}, verify=False)
    return json.loads(reload.text)
