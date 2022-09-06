from aiogram import executor
from aiogram_bot.misc.bot_connection import dp
from aiogram_bot.handlers import (
    chat_handler,
    reply_handler,
    inline_handler
)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
