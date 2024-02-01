import json

from configs.constants import BASE_API_URL
import requests


def city_doctor(hospital_id, token, search="", page=1):
    url = f"{BASE_API_URL}/users/doctor/?hospital_id={hospital_id}"
    reload = requests.get(url, headers={"content-type": "application/json", "Authorization": f"Token {token}"},
                          params={"search": search, 'page': page}, verify=False)
    return json.loads(reload.text)


def city_retrieve(city_id, token):
    url = f"{BASE_API_URL}/users/city/{city_id}/"
    reload = requests.get(url, headers={"Content-Type": "application/json", "Authorization": f"Token {token}"},
                          verify=False)
    return json.loads(reload.text)


def create_city(name=None, district=None, created_by=None, token=None):
    url = f"{BASE_API_URL}/users/city/"
    reload = requests.post(url, data=json.dumps({"name": name, "district": district, 'created_by': created_by}),
                           headers={"Content-Type": "application/json", "Authorization": f"Token {token}"},
                           verify=False)
    return reload.text

# print(create_city("Samarqand", 20, token="6c49382fc5c3c6e4ddf4393861586f78331c2e8f"))
