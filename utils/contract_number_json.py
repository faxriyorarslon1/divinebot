import json
from os.path import join as join_path
from pathlib import Path

# BASE_URL = Path(__file__).parent.parent
BASE_PATH = Path(__file__).parent
# print(BASE_PATH)

JSON_FILE = join_path(BASE_PATH, 'contract_number.json')


def write_contract_number():
    with open(JSON_FILE, 'r') as file:
        number = json.load(file)
    number['count'] += 1
    with open(JSON_FILE, 'w') as file:
        json.dump({'count': number['count']}, file)
    return number['count'] - 1

# print(write_contract_number())
