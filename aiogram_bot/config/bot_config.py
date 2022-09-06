import os
from aiogram_bot.config.app_config import DATABASE_DIR, RESOURCES_DIR


# --- BOT INFORMATION ---
BOT_TOKEN = 'your key'


# --- DATABASE ---
# jdbc:sqlite:D:/Work/TelegramBot/aiogram_bot/database/database.db
DATABASE_NAME = 'database.db'
DATABASE_PATH = os.path.join(DATABASE_DIR, DATABASE_NAME)
DATABASE_SQLALCHEMY_PATH = f'sqlite:///{DATABASE_PATH}'


# --- IMAGE RESOURCES ---
RESOURCES = 'images.xlsx'
RESOURCES_PATH = os.path.join(RESOURCES_DIR, RESOURCES)
