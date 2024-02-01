import datetime
import json

import requests

from configs.constants import BASE_API_URL
from utils.contract_number_json import write_contract_number


def order_delete(order_id, token):
    url = f"{BASE_API_URL}/order/order/{order_id}/"
    delete_order = requests.delete(url=url,
                                   headers={"Content-Type": "application/json", "Authorization": f"Token {token}"},
                                   verify=False)
    return delete_order.text


def order_create(products, inn, comment, total_price, type_price, token, is_manager_send, company_address,
                 company_name, bank_name, phone_number, status):
    url = f"{BASE_API_URL}/order/order/"
    create_order = None
    if status:
        create_order = requests.post(url, data=json.dumps(
            {"products": products, "inn": inn, "comment": comment, "total_price": total_price, "type_price": type_price,
             "is_manager_send": is_manager_send, 'company_address': company_address, "company_name": company_name,
             "bank_name": bank_name, "phone_number": phone_number, 'status': "office_manager"}),
                                     headers={"Content-Type": "application/json", "Authorization": f"Token {token}"},
                                     verify=False)
    else:
        create_order = requests.post(url, data=json.dumps(
            {"products": products, "inn": inn, "comment": comment, "total_price": total_price, "type_price": type_price,
             "is_manager_send": is_manager_send, 'company_address': company_address, "company_name": company_name,
             "bank_name": bank_name, "phone_number": phone_number}),
                                     headers={"Content-Type": "application/json", "Authorization": f"Token {token}"},
                                     verify=False)
    return create_order.text


def order_update(products, inn, comment, total_price, type_price, token, order_id, seller, is_manager_send):
    url = f"{BASE_API_URL}/order/order/{order_id}/"
    created_date = str(datetime.datetime.now())
    update_order = requests.put(url, data=json.dumps(
        {"products": products, "inn": inn, "comment": comment, "total_price": total_price, "type_price": type_price,
         "seller": seller, "is_manager_send": is_manager_send,
         'created_date': created_date, 'status': 'office_manager'}),
                                headers={"Content-Type": "application/json", "Authorization": f"Token {token}"},
                                verify=False)
    return update_order.text


def order_update_params(products, inn, comment, total_price, type_price, token, order_id, seller, is_manager_send):
    url = f"{BASE_API_URL}/order/order/{order_id}/"
    created_date = str(datetime.datetime.now())
    update_order = requests.put(url, data=json.dumps(
        {
            "products": products, "inn": inn, "comment": comment, "total_price": total_price, "type_price": type_price,
            "seller": seller, 'created_date': created_date}),
                                headers={"Content-Type": "application/json", "Authorization": f"Token {token}"},
                                verify=False)
    return update_order.text


def order_update_office_manager(products, inn, comment, total_price, type_price, token, order_id, seller,
                                is_manager_send):
    url = f"{BASE_API_URL}/order/order/{order_id}/"
    created_date = str(datetime.datetime.now())
    update_order = requests.put(url, data=json.dumps(
        {"products": products, "inn": inn, "comment": comment, "total_price": total_price, "type_price": type_price,
         "seller": seller, "is_manager_send": is_manager_send, 'status': 'office_manager',
         'created_date': created_date}),
                                headers={"Content-Type": "application/json", "Authorization": f"Token {token}"},
                                verify=False)
    return update_order.text


def get_order_contract_number(inn, company_name, token):
    url = f"{BASE_API_URL}/order/order/get_contract_number/"
    get_contract_number = requests.get(url=url, params={"inn": inn, 'company_name': company_name},
                                       headers={"Content-Type": "application/json", 'Authorization': f"Token {token}"},
                                       verify=False)
    return json.loads(get_contract_number.text)


def delivery_orders(token, page):
    url = f"{BASE_API_URL}/order/order/status_order/?page={page}"
    get_orders = requests.get(url=url, params={'status': "delivery"},
                              headers={"Content-Type": "application/json", 'Authorization': f"Token {token}"},
                              verify=False)
    return json.loads(get_orders.text)


def supplier_orders(token, page):
    url = f"{BASE_API_URL}/order/order/status_order/?page={page}"
    get_orders = requests.get(url=url, params={'status': "supplier"},
                              headers={"Content-Type": "application/json", 'Authorization': f"Token {token}"},
                              verify=False)
    return json.loads(get_orders.text)


def get_confirmed_orders(token, day, month):
    url = f"{BASE_API_URL}/order/order/order_confirmed_office_manager/"
    get_orders = requests.get(url=url, params={'day': day, 'month': month},
                              headers={"Content-Type": 'application/json', 'Authorization': f'Token {token}'},
                              verify=False)
    return json.loads(get_orders.text)


def get_confirmed_orders_office_manager(token, day, month):
    url = f"{BASE_API_URL}/order/order/order_confirmed_office_manager_send/"
    get_orders = requests.get(url=url, params={'day': day, 'month': month},
                              headers={"Content-Type": 'application/json', 'Authorization': f'Token {token}'},
                              verify=False)
    return json.loads(get_orders.text)


def get_not_agent_confirmed_orders(token):
    url = f"{BASE_API_URL}/order/order/not_send_manager_office_manager/"
    get_orders = requests.get(url=url, headers={"Content-Type": "application/json", "Authorization": f"Token {token}"},
                              verify=False)
    return json.loads(get_orders.text)


def get_agent_confirmed_orders(token):
    url = f"{BASE_API_URL}/order/order/send_manager_office_manager/"
    get_orders = requests.get(url=url, headers={"Content-Type": "application/json", "Authorization": f"Token {token}"},
                              verify=False)
    return json.loads(get_orders.text)


def get_unreviewed_orders(token, day, month):
    url = f"{BASE_API_URL}/order/order/order_unreviewed_office_manager/"
    get_orders = requests.get(url=url, params={'day': day, 'month': month},
                              headers={"Content-Type": 'application/json', 'Authorization': f'Token {token}'},
                              verify=False)
    return json.loads(get_orders.text)


def get_unreviewed_orders_office_manager(token, day, month):
    url = f"{BASE_API_URL}/order/order/order_unreviewed_office_manager_send/"
    get_orders = requests.get(url=url, params={'day': day, 'month': month},
                              headers={"Content-Type": 'application/json', 'Authorization': f'Token {token}'},
                              verify=False)
    return json.loads(get_orders.text)


def update_status(status, order_id, token):
    url = f"{BASE_API_URL}/order/order/{order_id}/status_update/"
    put_orders = requests.put(url=url, data=json.dumps({'status': status}),
                              headers={'content-type': "application/json", 'Authorization': f"Token {token}"},
                              verify=False)
    return json.loads(put_orders.text)


def set_order_contract_number(inn, token):
    url = f"{BASE_API_URL}/order/order/set_contract_number/"
    get_contract_number = requests.get(url=url, params={"inn": inn},
                                       headers={"Content-Type": "application/json", 'Authorization': f"Token {token}"},
                                       verify=False)
    return json.loads(get_contract_number.text)


def update_new_contract_number(order_id, token):
    url = f"{BASE_API_URL}/order/order/{order_id}/contract_number_update/"
    contract_number = str(write_contract_number())
    get_contract_number = requests.put(url=url, data=json.dumps({'contract_number': contract_number}),
                                       headers={"Content-Type": "application/json", 'Authorization': f"Token {token}"},
                                       verify=False)
    return json.loads(get_contract_number.text)


def update_hospital_residue(order_id,
                            token,
                            products,
                            inn,
                            total_price,
                            type_price,
                            seller,
                            is_manager_send,
                            created_date):  # TODO
    url = f"{BASE_API_URL}/order/order/{order_id}/create_excel_hospital_residue/"
    get_contract_number = requests.put(url=url, data=json.dumps(
        {"products": products, "inn": inn, "total_price": total_price, "type_price": type_price,
         "seller": seller, "is_manager_send": is_manager_send, 'status': 'office_manager',
         'created_date': created_date}),
                                       headers={"Content-Type": "application/json", 'Authorization': f"Token {token}"},
                                       verify=False)
    return json.loads(get_contract_number.text)


def order_get_all_order(token=None, page=1, search="", manager_send=True):
    url = f"{BASE_API_URL}/order/order/"
    get_all = requests.get(url, params={"page": page, "search": search, "manager_send": manager_send},
                           headers={"Content-Type": "application/json", "Authorization": f"Token {token}"},
                           verify=False)
    return json.loads(get_all.text)


def order_get_one_order(order_id, token):
    url = f"{BASE_API_URL}/order/order/{order_id}/"
    get_all = requests.get(url,
                           headers={"Content-Type": "application/json", "Authorization": f"Token {token}"},
                           verify=False)
    return json.loads(get_all.text)
