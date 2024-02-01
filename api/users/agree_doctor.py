import json

import requests

from configs.constants import BASE_API_URL


def agree_doctor_api(doctor=None, comment=None, check_agreement=None, created_by=None, token=None):
    url = f"{BASE_API_URL}/users/agree_doctor/"
    reload = requests.post(url=url,
                           data=json.dumps({"doctor": doctor, "comment": comment, "check_agreement": check_agreement,
                                            "created_by": created_by}),
                           headers={"Content-Type": "application/json", "Authorization": f"Token {token}"},
                           verify=False)
    return reload.text
