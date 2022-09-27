from typing import Type
from aiogram import types
from sqlalchemy import delete, update

from aiogram_bot.misc.db_connection import DBSession
from aiogram_bot.misc.bot_connection import bot

from aiogram_bot.models.message import Message
from aiogram_bot.models.user import User


async def get_actual_message(session: Type[DBSession], user_id: int):
    return session.query(Message).filter(Message.user_id == user_id).all()


async def delete_old_messages(session: Type[DBSession], messages: list):
    for message in messages:
        try:
            await bot.delete_message(message.chat_id, message.message_id)
            session.execute(delete(Message).filter(Message.message_id == message.message_id))
            session.commit()
        except Exception as e:
            print('delete old messages exc: ', e)
            session.execute(
                delete(Message).filter(Message.message_id == message.message_id)
            )
            session.commit()


async def reply_handler_set_defaults(session: Type[DBSession], message: types.Message, index: int, command: str):
    session.execute(update(User).where(User.user_id == message.from_user.id).values(last_index=index))
    session.commit()
    session.execute(update(User).where(User.user_id == message.from_user.id).values(last_reply_command=command))
    session.commit()
