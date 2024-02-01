import os
from datetime import datetime
from os.path import join as join_path

from os import remove

from configs.constants import BASE_URL

year = datetime.now().year
month = datetime.now().month
order_path = f"{year}{month}order.xlsx"
ORDER_EXCEL_PATH = join_path(BASE_URL, 'excel_utils', 'excel', 'order')
path = join_path(ORDER_EXCEL_PATH, order_path)


def check_excel(file_path, excel_path):
    try:
        with open(f'{join_path(file_path, excel_path)}', 'r') as file:
            return "bosingiz"
    except BaseException:
        return "file yoq"
