from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from configs.constants import BOT_TOKEN, STORAGE_PATH
from aiogram.contrib.fsm_storage.files import JSONStorage

storage = JSONStorage(STORAGE_PATH)
# PROXY_URL = "http://proxy.server:3128"
# PROXY_URL = "api.telegram.org:443"
bot = Bot(token=BOT_TOKEN, parse_mode='html')
dp = Dispatcher(bot, storage=storage)

if __name__ == '__main__':
    print(STORAGE_PATH)
