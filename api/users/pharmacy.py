import json

import requests

from configs.constants import BASE_API_URL


class Pharmacy:
    def __init__(self, pharmacy_id=None, name=None, city=None, address=None, token=None):
        self.pharmacy_id = pharmacy_id
        self.name = name
        self.address = address
        self.city = city
        self.token = token
        self.url = f"{BASE_API_URL}/hospital/pharmacy/"
        self.retrieve_url = f"{BASE_API_URL}/hospital/pharmacy/{self.pharmacy_id}/"

    def create(self):
        reload = requests.post(url=self.url,
                               data=json.dumps({"name": self.name, "city": self.city, 'address': self.address}),
                               headers={"Content-Type": "application/json", "Authorization": f"Token {self.token}"},
                               verify=False)
        return reload.text

    def retrieve(self):
        reload = requests.get(url=self.retrieve_url,
                              headers={"Content-Type": "application/json", "Authorization": f"Token {self.token}"},
                              verify=False)
        return json.loads(reload.text)

    def lists(self):
        reload = requests.get(url=self.url,
                              headers={"Content-Type": "application/json", "Authorization": f"Token {self.token}"},
                              params={"city": self.city}, verify=False)
        return json.loads(reload.text)

    def update(self):
        pass

    def destroy(self):
        pass
