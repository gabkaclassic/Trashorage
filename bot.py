from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
from settings import bot_token


bot = Bot(token=bot_token, parse_mode=ParseMode.HTML)
