import json

import requests

from configs.constants import BASE_API_URL
from os.path import join as join_path


class ResidueExcel:
    def __init__(self, path=None, name=None, token=None):
        self.path = path
        self.name = name
        self.token = token
        self.url = f'{BASE_API_URL}/users/hospital_residue_excel/'

    def get_last(self):
        path = requests.get(url=self.url,
                            headers={"Content-Type": "application/json", "Authorization": f"Token {self.token}"},
                            verify=False)
        return json.loads(path.text)['results'][-1]['path']

# residue_excel = ResidueExcel(token='2fbe191a233aa21142b1321fa6fe1d276c00866b').get_last()
# print(residue_excel)
