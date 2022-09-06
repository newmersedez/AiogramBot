from aiogram import types
from sqlalchemy import insert, delete, update

from aiogram_bot.keyboards.reply_keyboard import reply_keyboard
from aiogram_bot.keyboards.inline_keyboard import inline_main_design_keyboard

from aiogram_bot.models.user import User
from aiogram_bot.models.message import Message
from aiogram_bot.models.user_favorites import UserFavorites

from aiogram_bot.misc.bot_connection import dp, bot
from aiogram_bot.misc.db_connection import session_scope
from aiogram_bot.misc.resources_loader import ResourceType, ResourceLoader

from aiogram_bot.config.reply_commands import (
    SIMPLE_DESIGN_COMMAND,
    COMPLEX_DESIGN_COMMAND,
    FAVORITE_COMMAND,
    HELP_COMMAND
)
from aiogram_bot.config.text_defines import (
    DESIGN_STARTUP_TEXT,
    DESIGN_DESCRIPTION_TEXT,
    NO_FAVORITE_MESSAGE
)


@dp.message_handler(lambda message: message.text == SIMPLE_DESIGN_COMMAND)
async def reply_simple_design_command_handler(message: types.Message):
    with session_scope() as s:
        try:
            # Updating last index
            request = update(User).where(User.user_id == message.from_user.id).values(last_index=0)
            s.execute(request)

            # Updating last reply command
            request = update(User).where(User.user_id == message.from_user.id).values(last_reply_command=SIMPLE_DESIGN_COMMAND)
            s.execute(request)

            # Delete old messages
            await bot.delete_message(message.chat.id, message.message_id)
            request = s.query(Message).filter(Message.user_id == message.from_user.id).all()
            for result in request:
                await bot.delete_message(result.chat_id, result.message_id)
            request = delete(Message).where(Message.user_id == message.from_user.id)
            s.execute(request)

            # Set iteration index to zero
            request = update(User).where(User.user_id == message.from_user.id).values(last_index=0)
            s.execute(request)

            # Loading images from resources
            data = await ResourceLoader.load_resources(ResourceType.Simple)

            # Display messages and update message_id in Message table
            if data is not None and len(data) > 0:
                media = list()
                for i in range(1, 5):
                    media.append(types.InputMediaPhoto(data[i], f'Example {i}'))
                msg1_id = await bot.send_message(message.chat.id, DESIGN_STARTUP_TEXT, reply_markup=reply_keyboard)
                msg2_id = await bot.send_media_group(message.chat.id, media)
                msg3_id = await bot.send_message(message.chat.id, DESIGN_DESCRIPTION_TEXT.format(data[5], data[6]),
                                                 reply_markup=inline_main_design_keyboard)
                request = insert(Message).values(
                    [
                        {'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(msg1_id)},
                        *[{'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(elem)} for elem in msg2_id],
                        {'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(msg3_id)}
                    ]
                )
                s.execute(request)
        except Exception as e:
            print('EXCEPTION: ', e)


@dp.message_handler(lambda message: message.text == COMPLEX_DESIGN_COMMAND)
async def reply_complex_design_command_handler(message: types.Message):
    with session_scope() as s:
        try:
            # Updating last index
            request = update(User).where(User.user_id == message.from_user.id).values(last_index=0)
            s.execute(request)

            # Updating last reply command
            request = update(User).where(User.user_id == message.from_user.id).values(last_reply_command=COMPLEX_DESIGN_COMMAND)
            s.execute(request)

            # Delete old messages
            await bot.delete_message(message.chat.id, message.message_id)
            request = s.query(Message).filter(Message.user_id == message.from_user.id).all()
            for result in request:
                await bot.delete_message(result.chat_id, result.message_id)
            request = delete(Message).where(Message.user_id == message.from_user.id)
            s.execute(request)

            # Set iteration index to zero
            request = update(User).where(User.user_id == message.from_user.id).values(last_index=0)
            s.execute(request)

            # Loading images from resources
            data = await ResourceLoader.load_resources(ResourceType.Complex)

            # Display messages and update message_id in Message table
            if data is not None and len(data) > 0:
                media = list()
                for i in range(1, 5):
                    media.append(types.InputMediaPhoto(data[i], f'Example {i}'))
                msg1_id = await bot.send_message(message.chat.id, DESIGN_STARTUP_TEXT, reply_markup=reply_keyboard)
                msg2_id = await bot.send_media_group(message.chat.id, media)
                msg3_id = await bot.send_message(message.chat.id, DESIGN_DESCRIPTION_TEXT.format(data[5], data[6]),
                                                 reply_markup=inline_main_design_keyboard)
                request = insert(Message).values(
                    [
                        {'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(msg1_id)},
                        *[{'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(elem)} for elem in msg2_id],
                        {'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(msg3_id)}
                    ]
                )
                s.execute(request)
        except Exception as e:
            print('EXCEPTION: ', e)


@dp.message_handler(lambda message: message.text == FAVORITE_COMMAND)
async def reply_favorite_command_handler(message: types.Message):
    pass


@dp.message_handler(lambda message: message.text == HELP_COMMAND)
async def reply_help_command_handler(message: types.Message):
    pass
