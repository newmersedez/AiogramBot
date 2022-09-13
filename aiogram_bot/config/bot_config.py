import os
import configparser
from aiogram_bot.config.app_config import CONFIG_DIR, DATABASE_DIR, RESOURCES_DIR

# Read config file
parser = configparser.ConfigParser()
parser.read(os.path.join(CONFIG_DIR, 'bot_settings.ini'))


# --- BOT INFORMATION ---
BOT_TOKEN = parser.get('BOT_CONFIG', 'BOT_TOKEN')


# --- DATABASE ---
DATABASE_NAME = 'database.db'
DATABASE_PATH = os.path.join(DATABASE_DIR, DATABASE_NAME)
DATABASE_SQLALCHEMY_PATH = f'sqlite:///{DATABASE_PATH}'


# --- IMAGE RESOURCES ---
RESOURCES = 'images.xlsx'
RESOURCES_PATH = os.path.join(RESOURCES_DIR, RESOURCES)
