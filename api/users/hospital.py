import json

import requests

from configs.constants import BASE_API_URL
from os.path import join as join_path


class Hospital:
    def __init__(self, hospital_id=None, name=None, city=None, token=None):
        self.hospital_id = hospital_id
        self.name = name
        self.city = city
        self.token = token
        self.url = f"{BASE_API_URL}/hospital/hospital/"
        self.retrieve_url = f"{BASE_API_URL}/hospital/hospital/{self.hospital_id}/"

    def create(self):
        reload = requests.post(url=self.url, data=json.dumps({"name": self.name, "city": self.city}),
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
