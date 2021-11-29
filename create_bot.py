from bot_token import b_token
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage


storage = MemoryStorage()
bot = Bot(token=b_token)
dp = Dispatcher(bot, storage=storage)
