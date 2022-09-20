import os
import configparser
from aiogram import Dispatcher, Bot
from aiogram_bot.config import CONFIG_DIR

parser = configparser.ConfigParser()
parser.read(os.path.join(CONFIG_DIR, 'bot_config.ini'))

BOT_TOKEN = parser.get('BOT_CONFIG', 'bot_token')
BOT_ADMIN = int(parser.get('BOT_CONFIG', 'bot_admin'))

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)
