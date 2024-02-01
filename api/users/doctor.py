import json

import requests

from api.users import BASE


def create_doctor(name=None, phone_number=None, type_doctor=None,
                  category_doctor=None, hospital=None, token=None):
    url = f"{BASE}/doctor/"
    reload = requests.post(url=url, data=json.dumps(
        {"name": name,
         "phone_number": phone_number, "type_doctor": type_doctor,
         "category_doctor": category_doctor, "hospital": hospital}),
                           headers={"Content-Type": "application/json", "Authorization": f"Token {token}"},
                           verify=False)

    return reload.text


def doctor_retrieve(doctor_id, token):
    url = f"{BASE}/doctor/{doctor_id}/"
    reload = requests.get(url=url, headers={"Content-Type": "application/json", "Authorization": f"Token {token}"},
                          verify=False)
    return json.loads(reload.text)
