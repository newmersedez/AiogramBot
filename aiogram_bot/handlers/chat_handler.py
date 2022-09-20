from aiogram import types, filters
from sqlalchemy import insert

from aiogram_bot.misc import BOT_ADMIN
from aiogram_bot.models import User, Message
from aiogram_bot.keyboards import reply_keyboard
from aiogram_bot.misc import dp, bot, session_scope
from aiogram_bot.commands import STARTUP_TEXT, GREETING_USER_TEXT, ADMIN_AUTH_MESSAGE_TEXT
from aiogram_bot.handlers import delete_old_messages, get_actual_message


@dp.message_handler(filters.CommandStart())
async def chat_start_command_handler(message: types.Message):
    try:
        with session_scope() as s:
            if message.from_user.id == BOT_ADMIN:
                await bot.send_message(BOT_ADMIN, ADMIN_AUTH_MESSAGE_TEXT)
                return

            # Check if user in database
            user = s.query(User).filter(User.user_id == message.from_user.id).first()
            if user is None:
                s.execute(
                    insert(User).values(
                        user_id=message.from_user.id,
                        username=message.from_user.username,
                        last_index=0,
                        last_reply_command=None,
                        last_keyboard=None,
                        check_image_overview=0
                    )
                )

            # Get actual messages
            old_messages = await get_actual_message(s, message.from_user.id)

            # Add new user messages
            msg1_id = await bot.send_message(message.chat.id, STARTUP_TEXT)
            msg2_id = await bot.send_message(
                message.chat.id, GREETING_USER_TEXT.format(message.from_user.username), reply_markup=reply_keyboard)
            request = insert(Message).values(
                [
                    {'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(msg1_id)},
                    {'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(msg2_id)}
                ]
            )
            s.execute(request)

            # Delete old messages
            await bot.delete_message(message.chat.id, message.message_id)
            await delete_old_messages(s, old_messages)
    except Exception as e:
        print('EXC: ', e)
        await bot.delete_message(message.chat.id, message.message_id)
        pass
