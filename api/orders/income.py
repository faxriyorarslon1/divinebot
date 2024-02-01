import json

import requests

from configs.constants import BASE_API_URL


class Income:
    def __init__(self, token=None, image=None, file_name=None, day=None, month=None):
        self.token = token
        self.image = image
        self.file_name = file_name
        self.day = day
        self.month = month
        self.url = f"{BASE_API_URL}/users/income/"

    def create(self):
        requests.post(headers={"Content-Type": "Application/json", "Authorization": f"Token {self.token}"},
                      url=self.url, data=json.dumps({"image": self.image, "file_name": self.file_name}), verify=False)
        return "Success"

    def get_excel(self):
        payload = requests.get(url=self.url, params={'day': self.day, 'month': self.month},
                               headers={"Content-Type": "Application/json", 'Authorization': f"Token {self.token}"},
                               verify=False)
        if json.loads(payload.text)['results']:
            return json.loads(payload.text)['results'][-1]
        return None
