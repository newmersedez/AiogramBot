from aiogram import types
from sqlalchemy import insert, delete

from aiogram_bot.keyboards.reply_keyboard import reply_keyboard

from aiogram_bot.models.user import User
from aiogram_bot.models.message import Message

from aiogram_bot.misc.bot_connection import dp, bot
from aiogram_bot.misc.db_connection import session_scope

from aiogram_bot.config.chat_commands import START_COMMAND
from aiogram_bot.config.text_defines import STARTUP_TEXT, GREETING_USER_TEXT


@dp.message_handler(commands=START_COMMAND)
async def chat_start_command_handler(message: types.Message):
    with session_scope() as s:
        try:
            # Check if user in database
            user = s.query(User).filter(User.user_id == message.from_user.id).first()
            if user is None:
                request = insert(User).values(
                    user_id=message.from_user.id,
                    username=message.from_user.username,
                    last_index=0,
                    last_reply_command=None
                )
                s.execute(request)

            # Delete old user messages
            await bot.delete_message(message.chat.id, message.message_id)
            request = s.query(Message).filter(Message.user_id == message.from_user.id).all()
            for result in request:
                await bot.delete_message(result.chat_id, result.message_id)
            request = delete(Message).where(Message.user_id == message.from_user.id)
            s.execute(request)

            # Add new user messages
            msg1_id = await bot.send_message(message.chat.id, STARTUP_TEXT)
            msg2_id = await bot.send_message(message.chat.id, GREETING_USER_TEXT.format(message.from_user.username),
                                             reply_markup=reply_keyboard)
            request = insert(Message).values(
                [
                    {'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(msg1_id)},
                    {'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(msg2_id)}
                ]
            )
            s.execute(request)
        except Exception as e:
            print('EXCEPTION: ', e)
