import os
from aiogram_bot.config.app_config import RESOURCES_DIR


# --- BOT INFORMATION ---
BOT_TOKEN = 'Your token'


# --- DATABASE ---
DATABASE_NAME = 'database.db'
DATABASE_SQLALCHEMY_PATH = f'sqlite:///{DATABASE_NAME}'
DATABASE_PATH = os.path.join(RESOURCES_DIR, DATABASE_NAME)


# --- IMAGE RESOURCES ---
RESOURCES = 'images.xlsx'
RESOURCES_PATH = os.path.join(RESOURCES_DIR, RESOURCES)
