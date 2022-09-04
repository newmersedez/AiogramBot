from aiogram import Dispatcher, Bot
from aiogram_bot.config.bot_config import BOT_TOKEN


bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)
