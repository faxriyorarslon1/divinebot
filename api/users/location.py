import json

import requests
from datetime import datetime

from configs.constants import BASE_API_URL
from utils.date_time import date_time_check, admin_send_location_user

BASE = f"{BASE_API_URL}/users"


def get_all_location(user_id, token):
    url = f"{BASE}/location/"
    start_time, end_time = date_time_check()
    if start_time and end_time:
        reload = requests.get(
            url=url, params={"start": start_time, "end": end_time, "user": user_id},
            headers={"content-type": "application/json", "Authorization": f"Token {token}"},
            verify=False
        )
        return json.loads(reload.text)
    return {'count': 1}


def get_all_location_user(user_id):
    url = f"{BASE}/location/"
    start_time, end_time = admin_send_location_user()
    if start_time and end_time:
        reload = requests.get(url=url, params={"start": start_time, "end": end_time, "user_id": user_id},
                              headers={"content-type": "application/json"},
                              verify=False
                              )
        return json.loads(reload.text)
    return {'count': 1}


def get_location_member(user_id, token, day, year, month):
    url = f"{BASE}/location/get_day_location/"
    reload = requests.get(url=url, headers={"Content-Type": "application/json", "Authorization": f"Token {token}"},
                          params={"user_id": user_id, 'day': day, 'year': year, 'month': month}, verify=False)
    return json.loads(reload.text)


def get_location_member_new(user_id, token, day, year, month):
    url = f"{BASE}/location/get_day_user_location/"
    reload = requests.get(url=url, headers={"Content-Type": "application/json", "Authorization": f"Token {token}"},
                          params={"user_id": user_id, 'day': day, 'year': year, 'month': month}, verify=False)
    return json.loads(reload.text)


def create_location(lan=None, lat=None, created_by=None, token=None):
    url = f"{BASE}/location/"
    reload = requests.post(url=url, data=json.dumps(
        {"lan": lan, "lat": lat, "created_by": created_by}
    ), headers={"Content-Type": "application/json", "Authorization": f"Token {token}"}, verify=False)

    return reload.text
