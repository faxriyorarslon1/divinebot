from environs import Env
from pathlib import Path
from os.path import join as join_path

BASE_URL = Path(__file__).parent.parent
# print(BASE_URL.parent.parent)
DATABASE_URL = join_path(BASE_URL.parent.parent.parent, 'var', 'www', 'DivineBase', 'db.sqlite3')
env = Env()
env.read_env()

# BOT_TOKEN = "6043950593:AAEcVCka-EsLk3bocmWSlOqpAkzAURuINSU"  # Divine `Bot
BOT_TOKEN = '5562028031:AAHhwjOM66h1ZKZxfq3naS77PZwq7_3a7BM'  # Future World Group
BOT_NAME = "Future World Group Bot"
STORAGE_PATH = join_path(BASE_URL, 'configs', 'mystates.json')
BASE_API_URL = "https://divines.uz/version1"
# BASE_API_URL = "https://dilshod22.pythonanywhere.com/version1"
# BASE_API_URL = "http://127.0.0.1:8000/version1"
# BASE_API_NOT_VERSION = 'http://127.0.0.1:8000'
BASE_API_NOT_VERSION = 'https://divines.uz'
# BASE_API_NOT_VERSION = 'http://dilshod22.pythonanywhere.com'
LOCAL_FILE_NAME = join_path(BASE_URL, "media")
