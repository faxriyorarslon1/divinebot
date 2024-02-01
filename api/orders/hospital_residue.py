import json

import requests

from configs.constants import BASE_API_URL


class HospitalResidue:
    def __init__(self, order_id=None, created_by=None, district=None, status=None, company=None, aknel_gel=None,
                 astarakson_1125=None, astarakson_562=None, astaryus=None, intrizol=None, livomed_tab=None,
                 livomed_sirop=None, renum_cap=None, stresson_cap=None, tavamed=None, x_plays_maz=None, seprazon=None,
                 entro_d_cap=True, entro_d_sashe=None, lamino_100=None, lamino_200=None, token=None, page=None):
        self.created_by = created_by
        self.district = district
        self.status = status
        self.company = company
        self.aknel_gel = aknel_gel
        self.astarakson_1125 = astarakson_1125
        self.astarakson_562 = astarakson_562
        self.astaryus = astaryus
        self.intrizol = intrizol
        self.livomed_tab = livomed_tab
        self.livomed_sirop = livomed_sirop
        self.renum_cap = renum_cap
        self.stresson_cap = stresson_cap
        self.tavamed = tavamed
        self.x_plays_maz = x_plays_maz
        self.seprazon = seprazon
        self.entro_d_cap = entro_d_cap
        self.entro_d_sashe = entro_d_sashe
        self.lamino_100 = lamino_100
        self.lamino_200 = lamino_200
        self.order_id = order_id
        self.token = token
        self.page = page
        self.path = f"{BASE_API_URL}/hospital/hospital_vizit_residue/"
        self.retrieve_url = f"{BASE_API_URL}/hospital/hospital_vizit_residue/{self.order_id}/"

    def create(self):
        requests.post(url=self.path, data=json.dumps(
            {
                "created_by": self.created_by,
                'district': self.district,
                'status': 'office_manager',
                'company': self.company,

                'aknel_gel': self.aknel_gel,
                'astarakson_1125': self.astarakson_1125,
                'astarakson_562': self.astarakson_562,
                'astaryus': self.astaryus,
                'intrizol': self.intrizol,
                'livomed_tab': self.livomed_tab,
                'livomed_sirop': self.livomed_sirop,
                'renum_cap': self.renum_cap,
                'stresson_cap': self.stresson_cap,
                'tavamed': self.tavamed,
                'x_payls_maz': self.x_plays_maz,
                'seprazon': self.seprazon,
                'entro_d_cap': self.entro_d_cap,
                'entro_d_sashe': self.entro_d_sashe,
                'lamino_100': self.lamino_100,
                'lamino_200': self.lamino_200
            }),
                      headers={"Content-Type": "Application/json", "Authorization": f"Token {self.token}"},
                      verify=False)
        return "Success"

    def update(self):
        requests.put(url=self.retrieve_url, data=json.dumps(
            {
                'status': self.status,
                "created_by": self.created_by,
                'district': self.district,
                'company': self.company,
                'aknel_gel': self.aknel_gel,
                'astarakson_1125': self.astarakson_1125,
                'astarakson_562': self.astarakson_562,
                'astaryus': self.astaryus,
                'intrizol': self.intrizol,
                'livomed_tab': self.livomed_tab,
                'livomed_sirop': self.livomed_sirop,
                'renum_cap': self.renum_cap,
                'stresson_cap': self.stresson_cap,
                'tavamed': self.tavamed,
                'x_plays_maz': self.x_plays_maz,
                'seprazon': self.seprazon,
                'entro_d_cap': self.entro_d_cap,
                'entro_d_sashe': self.entro_d_sashe,
                'lamino_100': self.lamino_100,
                'lamino_200': self.lamino_200,

            }
        ),
                     headers={"Content-Type": "Application/json", "Authorization": f"Token {self.token}"},
                     verify=False)
        return "Success"

    def hospital_user_vizit(self):
        query = requests.get(url=f'{self.path}hospital_user_create_vizit/',
                             params={'company': self.company},
                             headers={'Content-Type': 'Application/json', 'Authorization': f'Token {self.token}'},
                             verify=False)
        return json.loads(query.text)

    def get_all(self):
        query = requests.get(url=self.path,
                             params={'page': self.page},
                             headers={"Content-Type": "Application/json", "Authorization": f"Token {self.token}"},
                             verify=False)
        return json.loads(query.text)

    def get_one(self):
        query = requests.get(url=self.retrieve_url,
                             headers={"Content-Type": "Application/json", "Authorization": f"Token {self.token}"},
                             verify=False)
        return json.loads(query.text)
