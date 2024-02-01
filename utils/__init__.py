import datetime
import json

from api.users import district_post


def village(lists):
    for l in lists:
        district_post(l)
    return True


vil = [
    "Andijon",
    "Buxoro",
    "Farg'ona",
    "Jizzax",
    "Namangan",
    "Navoiy",
    "Qashqadaryo",
    "Qoraqalpog'iston",
    "Samarqand",
    "Sirdaryo",
    "Surxandaryo",
    "Xorazm",
    "Toshkent Vil",
    # "Toshkent Shaxar",
]
# village(vil)
import requests


def requests_facture():
    url = "https://account.faktura.uz/token"
    grant_type = "password"
    try:
        reload = requests.post(url=url,
                               data={"grant_type": grant_type, "username": "998909972900", "password": "fwgfactura",
                                     "client_id": '998909972900',
                                     "client_secret": "aCMaZxb8aN8RmOH7CuaEz76WUDKtaIKdzKNn0SKrPZJ4m0uebDkalukN8ngP"},
                               headers={"Content-Type": "application/json"})

        return json.loads(reload.text)
    except Exception:
        return {"message": "Error"}


#
#
stir = "201080085"


# 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

def get_company(stir):
    url = f"https://api.faktura.uz/Api/Company/GetCompanyBasicDetails?companyInn={stir}"
    facture = requests_facture()
    if facture.get("message"):
        return {"message": "Error"}
    access_token = facture['access_token']
    try:
        reload = requests.get(url=url,
                              headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"})
        with open("data.json", 'w') as file:
            json.dump(json.loads(reload.text), file, indent=4)
            return json.loads(reload.text)
    except Exception:
        return {"message": "Error"}


def split_text(text: str):
    text = text.split('"')
    if len(text) >= 2:
        return text[1:]
    return text[0]
