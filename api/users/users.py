import json

import requests

from configs.constants import BASE_API_URL

BASE = f"{BASE_API_URL}/users"


def update_user(
        first_name=None,
        last_name=None,
        phone_number=None,
        passport_image_path=None,
        district=None,
        user_id=None,
        chat_id=None
):
    url = f'{BASE}/user/{user_id}/'
    payload = requests.put(url=url, data=json.dumps({
        "first_name": first_name,
        "last_name": last_name,
        "phone_number": phone_number,
        "passport_image_path": passport_image_path,
        "district": district,
        "chat_id": chat_id
    }), verify=False,
                           headers={"Content-Type": "application/json"}
                           )
    return payload.text


def create_user(first_name=None,
                last_name=None,
                phone_number=None,
                passport_image_path=None,
                district=None,
                is_member=None,
                chat_id=None
                ):
    url = f'{BASE}/user/'
    payload = requests.post(url=url, data=json.dumps({
        "first_name": first_name,
        "last_name": last_name,
        "phone_number": phone_number,
        "passport_image_path": passport_image_path,
        "district": district,
        "is_member": is_member,
        "chat_id": chat_id
    }), headers={"Content-Type": "application/json"}, verify=False)
    return payload.text


def login_user(phone_number):
    url = f'{BASE}/registration/login/'
    payload = requests.post(url=url, data=json.dumps({"phone_number": phone_number}),
                            headers={"Content-Type": "application/json"}, verify=False)
    return json.loads(payload.text)


def login_exist_user(phone_number):
    url = f"{BASE}/user/login_exist_user/"
    payload = requests.post(url=url, data=json.dumps({"phone_number": phone_number}),
                            headers={"Content-Type": "application/json"}, verify=False)
    return json.loads(payload.text)


def get_user_phone_number(phone_number):
    url = f'{BASE}/user/user_exist/'
    payload = requests.post(url=url, data=json.dumps({"phone_number": phone_number}),
                            headers={"Content-Type": "application/json"}, verify=False)
    return json.loads(payload.text)


def get_mp_users(district, first_name, token, page):
    url = f"{BASE}/user/mp_agent_all/"
    payload = requests.get(url=url, params={"district": district, 'first_name': first_name, 'page': page},
                           headers={'Content-Type': "Application/json", "Authorization": f"Token {token}"},
                           verify=False)
    return json.loads(payload.text)


def get_user_location(district):
    url = f"{BASE}/user/get_all_user_for_location/"
    payload = requests.get(url=url, verify=False, headers={'Content-Type': 'Application/json'},
                           params={'district': district})
    return payload.json()


def get_agent():
    url = f"{BASE}/user/get_all_agent/"
    payload = requests.get(url=url, verify=False, headers={'Content-Type': 'Application/json'})
    return payload.json()


def get_office_managers():
    url = f"{BASE}/user/get_all_office_manager/"
    payload = requests.get(url=url, verify=False, headers={'Content-Type': 'Application/json'})
    return payload.json()


def get_agent_vizits(district):
    url = f"{BASE}/user/get_all_agent_vizit/"
    payload = requests.get(url=url, verify=False, headers={'Content-Type': 'Application/json'},
                           params={'district': district})
    return payload.json()


# print(get_user_location())


def get_manager_users(district, token, page):
    url = f"{BASE}/user/admin_district_manager_user/"
    payload = requests.get(url=url, params={"district": district, 'page': page},
                           headers={'Content-Type': "Application/json", "Authorization": f"Token {token}"},
                           verify=False)
    return json.loads(payload.text)


def get_all_user_or_agent(district):
    url = f"{BASE}/user/"
    payload = requests.get(url=url, params={"district": district}, verify=False)
    # with open('data.json', 'w') as file:
    #     json.dump(json.loads(payload.text), file, indent=2)
    return json.loads(payload.text)


def get_all_not_active_member():
    url = f"{BASE}/user/get_all_not_active/"
    payload = requests.get(url=url, verify=False)
    return json.loads(payload.text)


def get_role_member(role):
    url = f"{BASE}/user/get_role_user/"
    payload = requests.get(url=url, params={"role": role}, verify=False)
    return json.loads(payload.text)


def get_one_user(user_id):
    url = f"{BASE}/user/{user_id}/"
    payload = requests.get(url=url, verify=False)
    return json.loads(payload.text)


# print(get_one_user(7))


def get_chat_id(chat_id):
    url = f"{BASE}/user/user_chat_id/"
    payload = requests.get(url=url, data=json.dumps({"chat_id": chat_id}),
                           headers={"Content-Type": "application/json"}, verify=False)
    return json.loads(payload.text)


# print(get_chat_id(str(1995492287)))


def update_user_is_member(user_id, role):
    is_member = True
    url = f"{BASE}/registration/{user_id}/"
    payload = requests.put(url=url, data=json.dumps({'is_member': is_member, "role": role}), verify=False,
                           headers={"content-type": "application/json"})
    return json.loads(payload.text)


def update_user_district(user_id, district):
    is_member = True
    url = f"{BASE}/user/{user_id}/district_update/"
    payload = requests.put(url=url, data=json.dumps({"district": district}),
                           verify=False,
                           headers={"content-type": "application/json"})
    return json.loads(payload.text)


def update_user_data_and_phone_number(user_id, first_name, last_name, phone_number):
    url = f"{BASE}/user/{user_id}/put_user_data_and_phone_number/"
    if last_name:
        payload = requests.put(url=url, data=json.dumps(
            {"first_name": first_name, 'last_name': last_name, 'phone_number': phone_number}),
                               verify=False,
                               headers={"content-type": "application/json"})
    else:
        payload = requests.put(url=url, data=json.dumps(
            {"first_name": first_name, 'phone_number': phone_number}),
                               verify=False,
                               headers={"content-type": "application/json"})
    return json.loads(payload.text)


def delete_user(user_id):
    url = f"{BASE}/user/{user_id}/"
    requests.delete(url=url, verify=False)
    return "Success"
