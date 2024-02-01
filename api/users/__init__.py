import json

from configs.constants import BASE_API_URL
import requests

BASE = f"{BASE_API_URL}/users"


def district_post(name):
    url = f"{BASE_API_URL}/users/district/"
    post = requests.post(url=url, data=json.dumps({"name": name}), headers={"Content-Type": "application/json"},
                         verify=False)
    return post.text


def district_delete(district_id):
    url = f"{BASE_API_URL}/users/district/{district_id}"
    delete = requests.delete(url, verify=False)
    return delete.text


def district_get_all():
    url = f"{BASE_API_URL}/users/district/"
    get_all = requests.get(url, verify=False)
    return json.loads(get_all.text)


# print(district_get_all())
def all_city_for_district(district_id, created_by, token, search=""):
    url = f"{BASE_API_URL}/users/city/?district_id={district_id}"
    get_all = requests.get(url, headers={"Authorization": f"Token {token}"},
                           params={"search": search, 'created_by': created_by}, verify=False)
    return json.loads(get_all.text)


def district_retrieve(district):
    url = f"{BASE_API_URL}/users/district/{district}/"
    get_all = requests.get(url, verify=False)
    return json.loads(get_all.text)
# print(all_city_for_district(20, "6c49382fc5c3c6e4ddf4393861586f78331c2e8f"))
