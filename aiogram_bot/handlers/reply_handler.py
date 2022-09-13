import requests
from aiogram import types
from urllib.parse import urlencode
from sqlalchemy import insert, update, and_

from image_utility import create_simple_template, create_complex_template

from aiogram_bot.config import IMAGES_DIR
from aiogram_bot.models import Message, User, UserFavorites
from aiogram_bot.handlers import reply_handler_set_defaults, get_actual_message, delete_old_messages
from aiogram_bot.misc import dp, bot, session_scope, ResourceType, ResourceLoader

from aiogram_bot.keyboards import (
    reply_keyboard,
    design_keyboard,
    favorite_keyboard,
    help_keyboard,
    upload_image_keyboard
)
from aiogram_bot.commands import (
    SIMPLE_DESIGN_COMMAND,
    COMPLEX_DESIGN_COMMAND,
    FAVORITE_COMMAND,
    HELP_COMMAND,

    DESIGN_STARTUP_TEXT,
    DESIGN_DESCRIPTION_TEXT,
    NO_FAVORITE_MESSAGE_TEXT,
    HELP_DESCRIPTION_TEXT,
    HELP_STARTUP_TEXT,
    HELP_WARNING_TEXT,
    UPLOAD_PHOTO_SUCCESS_TEXT,
    UPLOAD_PHOTO_FINISHED_TEXT
)


@dp.message_handler(content_types=['photo', 'document'])
async def photo_or_doc_handler(message: types.Message):
    try:
        with session_scope() as s:
            user_request = s.query(User).filter(User.user_id == message.from_user.id).first()
            if user_request.check_image_overview == 0:
                await bot.delete_message(message.chat.id, message.message_id)
                return

            if message.content_type == 'photo':
                await message.photo[-1].download(destination_file=fr'{IMAGES_DIR}\{message.from_user.id}.png')
            elif message.content_type == 'document':
                file_extension = message.document.file_name.split('.')[1]
                if file_extension not in ('png', 'jpg', 'bmp'):
                    await bot.delete_message(message.chat.id, message.message_id)
                    return
                await message.document.download(destination_file=fr'{IMAGES_DIR}\{message.from_user.id}.png')
            s.execute(
                insert(Message).values(
                    user_id=message.from_user.id,
                    chat_id=message.chat.id,
                    message_id=int(message.message_id)
                )
            )

            # Creating image
            print('lol1')
            user_request = s.query(User).filter(User.user_id == message.from_user.id).first()
            last_reply_command = user_request.last_reply_command
            image_path = fr'{IMAGES_DIR}\{message.from_user.id}.png'
            output_path = fr'{IMAGES_DIR}\{message.from_user.id}_result.png'
            template_path = fr'{IMAGES_DIR}\{message.from_user.id}_template.png'
            print('lol2')
            data = None
            if last_reply_command == FAVORITE_COMMAND:
                data, _ = await ResourceLoader.load_favorites(message.from_user.id, user_request.last_index)
                user_request = s.query(UserFavorites).filter(
                    and_(UserFavorites.user_id == message.from_user.id,
                         UserFavorites.resource == ','.join(elem.strip() for elem in data))
                ).first()
                last_reply_command = user_request.resource_type
            print('lol3')
            if data is None:
                if last_reply_command == SIMPLE_DESIGN_COMMAND:
                    data, _ = await ResourceLoader.load_images(ResourceType.Simple, user_request.last_index)
                elif last_reply_command == COMPLEX_DESIGN_COMMAND:
                    data, _ = await ResourceLoader.load_images(ResourceType.Complex, user_request.last_index)

            print('lol 4')
            base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
            public_key = data[0]
            print(public_key)
            final_url = base_url + urlencode(dict(public_key=public_key))
            response = requests.get(final_url)
            print(response.json())
            download_url = response.json()['href']
            download_response = requests.get(download_url)
            with open(template_path, 'wb') as f:
                f.write(download_response.content)

            print('lalka')
            if last_reply_command == SIMPLE_DESIGN_COMMAND:
                create_simple_template(image_path, output_path, template_path)
            elif last_reply_command == COMPLEX_DESIGN_COMMAND:
                create_complex_template(image_path, output_path, template_path)
            print('kek')

            # Sending message to chat
            msg1_id = await bot.send_message(message.chat.id, UPLOAD_PHOTO_SUCCESS_TEXT, reply_markup=reply_keyboard)
            msg2_id = await bot.send_photo(message.chat.id, types.InputFile(output_path))
            msg3_id = await bot.send_message(message.chat.id, UPLOAD_PHOTO_FINISHED_TEXT, reply_markup=upload_image_keyboard)

            s.execute(insert(Message).values(
                [
                    {'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(msg1_id)},
                    {'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(msg2_id)},
                    {'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(msg3_id)}
                ]
            ))
    except Exception as e:
        print(e)
        pass


@dp.message_handler(lambda message: message.text not in
                    (SIMPLE_DESIGN_COMMAND, COMPLEX_DESIGN_COMMAND, FAVORITE_COMMAND, HELP_COMMAND))
async def reply_non_command_handler(message):
    await bot.delete_message(message.chat.id, message.message_id)


@dp.message_handler(lambda message: message.text == SIMPLE_DESIGN_COMMAND)
async def reply_simple_design_command_handler(message: types.Message):
    try:
        with session_scope() as s:
            # Set overview to True
            s.execute(update(User).filter(User.user_id == message.from_user.id).values(check_image_overview=0))

            # Handler defaults
            await reply_handler_set_defaults(s, message, 0, SIMPLE_DESIGN_COMMAND)

            # Get actual messages
            old_messages = await get_actual_message(s, message.from_user.id)

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
                s.execute(
                    update(User).where(User.user_id == message.from_user.id).values(last_keyboard='design_keyboard')
                )
                s.execute(
                    insert(Message).values(
                        [
                            {'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(msg1_id)},
                            *[{'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(elem)}
                              for elem in msg2_id],
                            {'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(msg3_id)}
                        ]
                    )
                )

            # Delete old messages
            await bot.delete_message(message.chat.id, message.message_id)
            await delete_old_messages(s, old_messages)
    except:
        pass


@dp.message_handler(lambda message: message.text == COMPLEX_DESIGN_COMMAND)
async def reply_complex_design_command_handler(message: types.Message):
    try:
        with session_scope() as s:
            # Set overview to True
            s.execute(update(User).filter(User.user_id == message.from_user.id).values(check_image_overview=0))

            # Handler defaults
            await reply_handler_set_defaults(s, message, 0, COMPLEX_DESIGN_COMMAND)

            # Get actual messages
            old_messages = await get_actual_message(s, message.from_user.id)

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
                s.execute(
                    update(User).where(User.user_id == message.from_user.id).values(last_keyboard='design_keyboard')
                )
                s.execute(
                    insert(Message).values(
                        [
                            {'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(msg1_id)},
                            *[{'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(elem)}
                              for elem in msg2_id],
                            {'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(msg3_id)}
                        ]
                    )
                )

            # Delete old messages
            await bot.delete_message(message.chat.id, message.message_id)
            await delete_old_messages(s, old_messages)
    except:
        pass


@dp.message_handler(lambda message: message.text == FAVORITE_COMMAND)
async def reply_favorite_command_handler(message: types.Message):
    try:
        with session_scope() as s:
            # Set overview to True
            s.execute(update(User).filter(User.user_id == message.from_user.id).values(check_image_overview=0))

            # Handler defaults
            await reply_handler_set_defaults(s, message, 0, FAVORITE_COMMAND)

            # Get actual messages
            old_messages = await get_actual_message(s, message.from_user.id)

            # Loading images from resources
            data, _ = await ResourceLoader.load_favorites(message.from_user.id)

            # Display messages and update message_id in Message table
            if data is not None and len(data) > 0:
                media = list()
                for i in range(1, 5):
                    media.append(types.InputMediaPhoto(data[i], f'Example {i}'))
                msg1_id = await bot.send_message(message.chat.id, DESIGN_STARTUP_TEXT, reply_markup=reply_keyboard)
                msg2_id = await bot.send_media_group(message.chat.id, media)
                msg3_id = await bot.send_message(
                    message.chat.id, DESIGN_DESCRIPTION_TEXT.format(data[5], data[6]), reply_markup=favorite_keyboard)
                s.execute(
                    update(User).where(User.user_id == message.from_user.id).values(last_keyboard='favorite_keyboard')
                )
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
                msg_id = await bot.send_message(message.chat.id, NO_FAVORITE_MESSAGE_TEXT, reply_markup=reply_keyboard)
                s.execute(
                    insert(Message).values(
                        user_id=message.from_user.id,
                        chat_id=message.chat.id,
                        message_id=int(msg_id)
                    )
                )

            # Delete old messages
            await bot.delete_message(message.chat.id, message.message_id)
            await delete_old_messages(s, old_messages)
    except:
        pass


@dp.message_handler(lambda message: message.text == HELP_COMMAND)
async def reply_help_command_handler(message: types.Message):
    try:
        with session_scope() as s:
            # Set overview to True
            s.execute(update(User).filter(User.user_id == message.from_user.id).values(check_image_overview=0))

            # Handler defaults
            await reply_handler_set_defaults(s, message, 0, HELP_COMMAND)

            # Get actual messages
            old_messages = await get_actual_message(s, message.from_user.id)

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
                s.execute(
                    update(User).where(User.user_id == message.from_user.id).values(last_keyboard='help_keyboard')
                )
                s.execute(
                    insert(Message).values(
                        [
                            {'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(msg1_id)},
                            {'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(msg2_id)},
                            *[{'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(elem)} for
                              elem in msg3_id],
                            {'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(msg4_id)}
                        ]
                    )
                )

            # Delete old messages
            await bot.delete_message(message.chat.id, message.message_id)
            await delete_old_messages(s, old_messages)
    except Exception as e:
        print(e)
        pass
