import json

import requests

from configs.constants import BASE_API_URL


class Company:
    def __init__(self, company_id=None, company_name=None, company_address=None, phone_number=None, bank_name=None,
                 token=None, search=None, page=None, inn=None, created_by=None, director_name=None,
                 director_phone=None, provider_name=None, provider_phone=None):
        self.company_id = company_id
        self.company_name = company_name
        self.company_address = company_address
        self.phone_number = phone_number
        self.bank_name = bank_name
        self.token = token
        self.search = search
        self.page = page
        self.inn = inn
        self.provider_name = provider_name
        self.director_name = director_name
        self.provider_phone = provider_phone
        self.director_phone = director_phone
        self.created_by = created_by
        self.path = f"{BASE_API_URL}/order/company/"
        self.retrieve_url = f"{BASE_API_URL}/order/company/{self.company_id}/"

    def create(self):
        requests.post(url=self.path, data=json.dumps(
            {"company_name": self.company_name, 'company_address': self.company_address,
             'phone_number': self.phone_number, 'bank_name': self.bank_name, 'inn': self.inn,
             'created_by': self.created_by}),
                      headers={"Content-Type": "Application/json", "Authorization": f"Token {self.token}"},
                      verify=False)
        return "Success"

    def get_all(self):
        reload = requests.get(url=self.path, params={"search": self.search, 'page': self.page},
                              headers={"Content-Type": "Application/json", "Authorization": f"Token {self.token}"},
                              verify=False)
        return json.loads(reload.text)

    def get_one(self):
        reload = requests.get(url=self.retrieve_url,
                              headers={"Content-Type": "Application/json", "Authorization": f"Token {self.token}"},
                              verify=False)
        return json.loads(reload.text)

    def update(self):
        get_one = requests.get(url=self.retrieve_url,
                               headers={"Content-Type": "Application/json", "Authorization": f"Token {self.token}"},
                               verify=False)
        # return json.loads(reload.text)
        data = json.loads(get_one.text)
        created_by = data.get('created_by')
        company_name = data.get('company_name')
        company_address = data.get('company_address')
        phone_number = data.get('phone_number')
        bank_name = data.get('bank_name')
        inn = data.get('inn')
        reload = requests.put(url=self.retrieve_url,
                              headers={'Content-Type': 'Application/json', 'Authorization': f'Token {self.token}'},
                              data=json.dumps({
                                  'company_name': company_name,
                                  'company_address': company_address,
                                  'bank_name': bank_name,
                                  'created_by': created_by,
                                  'phone_number': phone_number,
                                  'inn': inn,
                                  'company_director_name': self.director_name,
                                  'company_provider_name': self.provider_name,
                                  'company_provider_phone_number': self.provider_phone,
                                  'company_director_phone_number': self.director_phone,
                              }), verify=False)
        return json.loads(reload.text)
