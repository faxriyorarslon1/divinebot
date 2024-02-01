import json

import requests

from configs.constants import BASE_API_URL


def get_products(search="", page=1, token=None):
    url = f"{BASE_API_URL}/product/product/?page={page}"
    get_all_product = requests.get(url, params={"search": search},
                                   headers={"Content-Type": "application/json", "Authorization": f"Token {token}"},
                                   verify=False)
    return json.loads(get_all_product.text)


# print(get_products())


def get_all_products(token=None, page=1):
    url = f"{BASE_API_URL}/product/product/get_all/?page={page}"
    get_all_product = requests.get(url,
                                   headers={"Content-Type": "application/json", "Authorization": f"Token {token}"},
                                   verify=False)
    return json.loads(get_all_product.text)


def get_one_product(product_id, token=None):
    url = f"{BASE_API_URL}/product/product/{product_id}/"
    one_product = requests.get(url, headers={"Content-Type": "application/json", "Authorization": f"Token {token}"},
                               verify=False)
    return json.loads(one_product.text)


#
# print(get_one_product(1, token='2cd3f39c97b29241716baea47600736f39937065'))


def create_product(name: str = None, composition: str = None, count=None, original_count=None,
                   price1: float = None, price2: float = None,
                   expired_date: str = None, seria: str = None, active: bool = None, image: str = None, token=None):
    payload = requests.post(url=f"{BASE_API_URL}/product/product/",
                            data=json.dumps({"name": name, 'composition': composition, 'count': count,
                                             'original_count': original_count, 'price1': price1, 'price2': price2,
                                             'expired_date': expired_date, 'seria': seria, 'active': active,
                                             "image": image}),
                            headers={"Content-Type": "application/json", 'Authorization': f"Token {token}"},
                            verify=False)
    return json.loads(payload.text)


def update_product(name: str = None, composition: str = None, count: int = None, original_count: int = None,
                   price1: float = None, price2: float = None,
                   expired_date: str = None, seria: str = None, active: bool = None, image: str = None, product_id=None,
                   token=None, created_by=None, warehouse_count=None):
    data = json.dumps({"name": name, 'composition': composition, 'count': count,
                       'original_count': original_count, 'price1': price1, 'price2': price2,
                       'expired_date': expired_date, 'seria': seria, 'active': active,
                       "image": image, 'created_by': created_by})
    if warehouse_count:
        data = json.dumps({"name": name, 'composition': composition, 'count': count,
                           'original_count': original_count, 'price1': price1, 'price2': price2,
                           'expired_date': expired_date, 'seria': seria, 'active': active,
                           "image": image, 'created_by': created_by,
                           'warehouse_count': warehouse_count})
    payload = requests.put(url=f"{BASE_API_URL}/product/product/{product_id}/",
                           data=data,
                           headers={"Content-Type": "application/json", 'Authorization': f"Token {token}"},
                           verify=False)
    return json.loads(payload.text)


def delete_product(product_id, token):
    payload = requests.delete(url=f"{BASE_API_URL}/product/product/{product_id}/",
                              headers={"Content-Type": "application/json", 'Authorization': f"Token {token}"},
                              verify=False)
    return "Success"
