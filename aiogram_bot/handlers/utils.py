from typing import Type
from aiogram import types
from sqlalchemy import delete, update

from aiogram_bot.misc.db_connection import DBSession
from aiogram_bot.misc.bot_connection import bot

from aiogram_bot.models.message import Message
from aiogram_bot.models.user import User


async def delete_old_messages(session: Type[DBSession], message: types.Message):
    await bot.delete_message(message.chat.id, message.message_id)
    request = session.query(Message).filter(Message.user_id == message.from_user.id).all()
    for result in request:
        await bot.delete_message(result.chat_id, result.message_id)
    request = delete(Message).where(Message.user_id == message.from_user.id)
    session.execute(request)


async def reply_handler_set_defaults(session: Type[DBSession], message: types.Message, index: int, command: str):
    session.execute(update(User).where(User.user_id == message.from_user.id).values(last_index=index))
    session.execute(update(User).where(User.user_id == message.from_user.id).values(last_reply_command=command))
    await delete_old_messages(session, message)
