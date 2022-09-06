from aiogram import types
from sqlalchemy import insert

from aiogram_bot.models.message import Message

from aiogram_bot.handlers.utils import reply_handler_set_defaults
from aiogram_bot.keyboards.reply_keyboard import reply_keyboard
from aiogram_bot.keyboards.inline_keyboard import design_keyboard, favorite_keyboard, help_keyboard

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
    NO_FAVORITE_MESSAGE,
    HELP_DESCRIPTION_TEXT,
    HELP_STARTUP_TEXT,
    HELP_WARNING_TEXT
)


# noinspection PyBroadException
@dp.message_handler(lambda message: message.text == SIMPLE_DESIGN_COMMAND)
async def reply_simple_design_command_handler(message: types.Message):
    try:
        with session_scope() as s:
            # Handler defaults
            await reply_handler_set_defaults(s, message, 0, SIMPLE_DESIGN_COMMAND)

            # Loading images from resources
            data, _ = await ResourceLoader.load_images(ResourceType.Simple)

            # Display messages and update message_id in Message table
            if data is not None and len(data) > 0:
                media = list()
                for i in range(1, 5):
                    media.append(types.InputMediaPhoto(data[i], f'Example {i}'))
                msg1_id = await bot.send_message(message.chat.id, DESIGN_STARTUP_TEXT, reply_markup=reply_keyboard)
                msg2_id = await bot.send_media_group(message.chat.id, media)
                msg3_id = await bot.send_message(message.chat.id, DESIGN_DESCRIPTION_TEXT.format(data[5], data[6]),
                                                 reply_markup=design_keyboard)
                s.execute(insert(Message).values(
                    [
                        {'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(msg1_id)},
                        *[{'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(elem)}
                          for elem in msg2_id],
                        {'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(msg3_id)}
                    ]
                ))
    except:
        pass


# noinspection PyBroadException
@dp.message_handler(lambda message: message.text == COMPLEX_DESIGN_COMMAND)
async def reply_complex_design_command_handler(message: types.Message):
    try:
        with session_scope() as s:
            # Handler defaults
            await reply_handler_set_defaults(s, message, 0, COMPLEX_DESIGN_COMMAND)

            # Loading images from resources
            data, _ = await ResourceLoader.load_images(ResourceType.Complex)

            # Display messages and update message_id in Message table
            if data is not None and len(data) > 0:
                media = list()
                for i in range(1, 5):
                    media.append(types.InputMediaPhoto(data[i], f'Example {i}'))
                msg1_id = await bot.send_message(message.chat.id, DESIGN_STARTUP_TEXT, reply_markup=reply_keyboard)
                msg2_id = await bot.send_media_group(message.chat.id, media)
                msg3_id = await bot.send_message(message.chat.id, DESIGN_DESCRIPTION_TEXT.format(data[5], data[6]),
                                                 reply_markup=design_keyboard)
                request = insert(Message).values(
                    [
                        {'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(msg1_id)},
                        *[{'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(elem)}
                          for elem in msg2_id],
                        {'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(msg3_id)}
                    ]
                )
                s.execute(request)
    except:
        pass


# noinspection DuplicatedCode
@dp.message_handler(lambda message: message.text == FAVORITE_COMMAND)
async def reply_favorite_command_handler(message: types.Message):
    # noinspection PyBroadException
    try:
        with session_scope() as s:
            # Handler defaults
            await reply_handler_set_defaults(s, message, 0, FAVORITE_COMMAND)

            # Loading images from resources
            data, _ = await ResourceLoader.load_favorites(message.from_user.id)

            # Display messages and update message_id in Message table
            if data is not None and len(data) > 0:
                media = list()
                for i in range(1, 5):
                    media.append(types.InputMediaPhoto(data[i], f'Example {i}'))
                msg1_id = await bot.send_message(message.chat.id, DESIGN_STARTUP_TEXT, reply_markup=reply_keyboard)
                msg2_id = await bot.send_media_group(message.chat.id, media)
                msg3_id = await bot.send_message(message.chat.id, DESIGN_DESCRIPTION_TEXT.format(data[5], data[6]),
                                                 reply_markup=favorite_keyboard)
                request = insert(Message).values(
                    [
                        {'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(msg1_id)},
                        *[{'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(elem)} for
                          elem in msg2_id],
                        {'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(msg3_id)}
                    ]
                )
                s.execute(request)
            else:
                msg_id = await bot.send_message(message.chat.id, NO_FAVORITE_MESSAGE, reply_markup=reply_keyboard)
                request = insert(Message).values(
                    user_id=message.from_user.id,
                    chat_id=message.chat.id,
                    message_id=int(msg_id)
                )
                s.execute(request)
    except:
        pass


@dp.message_handler(lambda message: message.text == HELP_COMMAND)
async def reply_help_command_handler(message: types.Message):
    # noinspection PyBroadException
    try:
        with session_scope() as s:
            # Handler defaults
            await reply_handler_set_defaults(s, message, 0, HELP_COMMAND)

            # Loading images from resources
            data, _ = await ResourceLoader.load_images(ResourceType.Help)

            # Display messages and update message_id in Message table
            if data is not None and len(data) > 0:
                media = list()
                for i in range(0, 2):
                    media.append(types.InputMediaPhoto(data[i], f'Example {i}'))
                msg1_id = await bot.send_message(message.chat.id, HELP_STARTUP_TEXT, reply_markup=reply_keyboard)
                msg2_id = await bot.send_message(message.chat.id, HELP_WARNING_TEXT)
                msg3_id = await bot.send_media_group(message.chat.id, media)
                msg4_id = await bot.send_message(message.chat.id, HELP_DESCRIPTION_TEXT.format(data[2], data[3]),
                                                 reply_markup=help_keyboard)
                s.execute(insert(Message).values(
                    [
                        {'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(msg1_id)},
                        {'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(msg2_id)},
                        *[{'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(elem)} for
                          elem in msg3_id],
                        {'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(msg4_id)}
                    ]
                ))
    except:
        pass
