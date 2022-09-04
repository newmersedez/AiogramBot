from aiogram import executor
from aiogram_bot.misc.bot_connection import dp


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
