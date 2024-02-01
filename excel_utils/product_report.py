from os.path import join as join_path

from configs.constants import BASE_URL

PRODUCT_EXCEL_PATH = join_path(BASE_URL, 'excel_utils', 'excel', 'product')
DEBIT_EXCEL_PATH = join_path(BASE_URL, 'excel_utils', 'excel', 'debit')
CONTRACT_NUMBER_EXCEL_PATH = join_path(BASE_URL, 'excel_utils', 'excel', 'contract_number')
INCOME_EXCEL_PATH = join_path(BASE_URL, 'excel_utils', 'excel', 'income')
WRONG_FILE = join_path(BASE_URL, 'excel_utils', 'excel', 'wrong')
PRODUCT_IMAGE = join_path(BASE_URL, 'media')


def product_create_excel(file_name, content):
    excel_path = join_path(PRODUCT_EXCEL_PATH, file_name)
    with open(excel_path, 'wb') as file:
        file.write(content)
    return "Success"


def get_content_type(content_type: str):
    content = content_type.split('/')[-1]
    first = 0
    last = len(content)
    response = ""
    while first < last:
        if content[first] == ".":
            response += content[first:last]
        first += 1
    return response


def create_product_image(file_name, content, content_type):
    content_ = get_content_type(content_type)
    image_path = join_path(PRODUCT_IMAGE, file_name)
    with open(f'{image_path}{content_}', 'wb') as file:
        file.write(content)
    return "Success"


def debit_create_excel(file_name, content):
    excel_path = join_path(DEBIT_EXCEL_PATH, file_name)
    with open(excel_path, 'wb') as file:
        file.write(content)
    return "Success"


def contract_number_create_excel(file_name, content):
    excel_path = join_path(CONTRACT_NUMBER_EXCEL_PATH, file_name)
    with open(excel_path, 'wb') as file:
        file.write(content)
    return "Success"


def income_create_excel(file_name, content):
    excel_path = join_path(INCOME_EXCEL_PATH, file_name)
    with open(excel_path, 'wb') as file:
        file.write(content)
    return "Success"
