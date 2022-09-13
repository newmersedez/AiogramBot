import os


# --- PACKAGE ROOT PATH ---
ROOT_DIR = os.path.abspath(os.path.curdir)
AIOGRAM_BOT_PACKAGE_DIR = os.path.join(ROOT_DIR, 'aiogram_bot')


# --- DIR PATH ---
CONFIG_DIR = os.path.join(AIOGRAM_BOT_PACKAGE_DIR, 'config')
COMMANDS_DIR = os.path.join(AIOGRAM_BOT_PACKAGE_DIR, 'commands')
DATABASE_DIR = os.path.join(AIOGRAM_BOT_PACKAGE_DIR, 'database')
HANDLERS_DIR = os.path.join(AIOGRAM_BOT_PACKAGE_DIR, 'handlers')
KEYBOARDS_DIR = os.path.join(AIOGRAM_BOT_PACKAGE_DIR, 'keyboards')
MISC_DIR = os.path.join(AIOGRAM_BOT_PACKAGE_DIR, 'misc')
MODELS_DIR = os.path.join(AIOGRAM_BOT_PACKAGE_DIR, 'models')
RESOURCES_DIR = os.path.join(AIOGRAM_BOT_PACKAGE_DIR, 'resources')
IMAGES_DIR = os.path.join(AIOGRAM_BOT_PACKAGE_DIR, 'images')
