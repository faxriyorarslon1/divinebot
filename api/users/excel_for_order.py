import json

import requests

from api.users import BASE
from configs.constants import BASE_API_URL


class OrderExcel:
    def __init__(self, token=None, image=None, file_name=None):
        self.token = token
        self.image = image
        self.file_name = file_name
        self.url = f"{BASE}/order_excel/"

    def create(self):
        requests.post(headers={"Content-Type": "Application/json", "Authorization": f"Token {self.token}"},
                      url=self.url, data=json.dumps({"image": self.image, "file_name": self.file_name}), verify=False)
        return "Success"

    def get_excel(self):
        payload = requests.get(url=self.url,
                               headers={"Content-Type": "Application/json", 'Authorization': f"Token {self.token}"},
                               verify=False)
        if json.loads(payload.text)['count'] != 0:
            return json.loads(payload.text)['results'][-1]
        return None
