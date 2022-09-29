import requests
import os
from aiogram import types
from urllib.parse import urlencode
from sqlalchemy import insert, update, and_

from image_utility import create_simple_template, create_complex_template

from aiogram_bot.config import IMAGES_DIR
from aiogram_bot.models import Message, User, UserFavorites
from aiogram_bot.handlers import reply_handler_set_defaults, get_actual_message, delete_old_messages
from aiogram_bot.misc import dp, bot, ResourceType, ResourceLoader, DBSession

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
    EXAMPLES_COMMAND,

    DESIGN_STARTUP_TEXT,
    DESIGN_DESCRIPTION_TEXT,
    NO_FAVORITE_MESSAGE_TEXT,
    HELP_DESCRIPTION_TEXT,
    HELP_STARTUP_TEXT,
    HELP_WARNING_TEXT,
    UPLOAD_PHOTO_SUCCESS_TEXT,
    UPLOAD_PHOTO_FINISHED_TEXT,
    EXAMPLES_MESSAGE_TEXT
)


from threading import Lock
users_set = set()


@dp.message_handler(content_types=['voice', 'video'])
async def reply_non_image_send_handler(message: types.Message):
    await bot.delete_message(message.chat.id, message.message_id)


@dp.message_handler(content_types=['photo', 'document'])
async def reply_image_send_handler(message: types.Message):
    s = DBSession()
    try:
        user_request = s.query(User).filter(User.user_id == message.from_user.id).first()
        if user_request.check_image_overview == 0:
            await bot.delete_message(message.chat.id, message.message_id)
            return

        if message.content_type == 'photo':
            await message.photo[-1].download(destination_file=os.path.join(IMAGES_DIR, f'{message.from_user.id}.png'))
        elif message.content_type == 'document':
            file_extension = message.document.file_name.split('.')[1]
            if file_extension not in ('png', 'jpg', 'bmp'):
                await bot.delete_message(message.chat.id, message.message_id)
                return
            await message.document.download(destination_file=os.path.join(IMAGES_DIR, f'{message.from_user.id}.png'))
        s.execute(
            insert(Message).values(
                user_id=message.from_user.id,
                chat_id=message.chat.id,
                message_id=int(message.message_id)
            )
        )
        s.commit()

        # Creating image
        user_request = s.query(User).filter(User.user_id == message.from_user.id).first()
        last_reply_command = user_request.last_reply_command
        image_path = os.path.join(IMAGES_DIR, f'{message.from_user.id}.png')
        output_path = os.path.join(IMAGES_DIR, f'{message.from_user.id}_result.png')
        template_path = os.path.join(IMAGES_DIR, f'{message.from_user.id}_template.png')

        data = None
        if last_reply_command == FAVORITE_COMMAND:
            data, _ = await ResourceLoader.load_favorites(message.from_user.id, user_request.last_index)
            user_request = s.query(UserFavorites).filter(
                and_(UserFavorites.user_id == message.from_user.id,
                     UserFavorites.resource == ','.join(elem.strip() for elem in data))
            ).first()
            last_reply_command = user_request.resource_type

        if data is None:
            if last_reply_command == SIMPLE_DESIGN_COMMAND:
                data, _ = await ResourceLoader.load_images(ResourceType.Simple, user_request.last_index)
            elif last_reply_command == COMPLEX_DESIGN_COMMAND:
                data, _ = await ResourceLoader.load_images(ResourceType.Complex, user_request.last_index)

        base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
        public_key = data[0]
        final_url = base_url + urlencode(dict(public_key=public_key))
        response = requests.get(final_url)
        download_url = response.json()['href']
        download_response = requests.get(download_url)
        with open(template_path, 'wb') as f:
            f.write(download_response.content)

        if last_reply_command == SIMPLE_DESIGN_COMMAND:
            create_simple_template(image_path, output_path, template_path)
        elif last_reply_command == COMPLEX_DESIGN_COMMAND:
            create_complex_template(image_path, output_path, template_path)

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
        s.commit()
    except Exception as e:
        # print('exc: ', e)
        await bot.delete_message(message.chat.id, message.message_id)
    finally:
        s.close()


@dp.message_handler(lambda message: message.text not in
                    (SIMPLE_DESIGN_COMMAND, COMPLEX_DESIGN_COMMAND, FAVORITE_COMMAND, HELP_COMMAND, EXAMPLES_COMMAND))
async def reply_non_command_handler(message):
    await bot.delete_message(message.chat.id, message.message_id)


@dp.message_handler(lambda message: message.text == SIMPLE_DESIGN_COMMAND)
async def reply_simple_design_command_handler(message: types.Message):
    s = DBSession()
    try:
        if message.from_user.id in users_set:
            await bot.delete_message(message.chat.id, message.message_id)
            return
        else:
            users_set.add(message.from_user.id)

        # Get actual messages
        old_messages = await get_actual_message(s, message.from_user.id)

        # Loading images from resources
        data, _ = await ResourceLoader.load_images(ResourceType.Simple)

        # Display messages and update message_id in Message table
        data_check = ','.join(data)
        user_favorites = s.query(UserFavorites).filter(UserFavorites.user_id == message.from_user.id)
        in_favorite = False
        for fav in user_favorites:
            if data_check == fav.resource:
                in_favorite = True
                break

        if data is not None and len(data) > 0:
            media = list()
            for i in range(1, 5):
                media.append(types.InputMediaPhoto(data[i], f'Example {i}'))
            msg1_id = await bot.send_message(message.chat.id, DESIGN_STARTUP_TEXT, reply_markup=reply_keyboard)
            msg2_id = await bot.send_media_group(message.chat.id, media)
            if in_favorite:
                markup = 'favorite_keyboard'
                msg3_id = await bot.send_message(message.chat.id, DESIGN_DESCRIPTION_TEXT.format(data[5], data[6]),
                                                 reply_markup=favorite_keyboard)
            else:
                markup = 'design_keyboard'
                msg3_id = await bot.send_message(message.chat.id, DESIGN_DESCRIPTION_TEXT.format(data[5], data[6]),
                                                 reply_markup=design_keyboard)
            s.execute(
                update(User).where(User.user_id == message.from_user.id).values(last_keyboard=markup)
            )
            s.commit()
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
            s.commit()

        # Set overview to True
        s.execute(update(User).filter(User.user_id == message.from_user.id).values(check_image_overview=0))
        s.commit()

        # Handler defaults
        await reply_handler_set_defaults(s, message, 0, SIMPLE_DESIGN_COMMAND)

        # Delete old messages
        await bot.delete_message(message.chat.id, message.message_id)
        await delete_old_messages(s, old_messages)
    except Exception as e:
        # print('reply simple exc: ', e)
        await bot.delete_message(message.chat.id, message.message_id)
    finally:
        if message.from_user.id in users_set:
            users_set.remove(message.from_user.id)
        s.close()


@dp.message_handler(lambda message: message.text == COMPLEX_DESIGN_COMMAND)
async def reply_complex_design_command_handler(message: types.Message):
    s = DBSession()
    try:
        if message.from_user.id in users_set:
            await bot.delete_message(message.chat.id, message.message_id)
            return
        else:
            users_set.add(message.from_user.id)

        # Get actual messages
        old_messages = await get_actual_message(s, message.from_user.id)

        # Loading images from resources
        data, _ = await ResourceLoader.load_images(ResourceType.Complex)

        # Display messages and update message_id in Message table
        data_check = ','.join(data)
        user_favorites = s.query(UserFavorites).filter(UserFavorites.user_id == message.from_user.id)
        in_favorite = False
        for fav in user_favorites:
            if data_check == fav.resource:
                in_favorite = True
                break

        if data is not None and len(data) > 0:
            media = list()
            for i in range(1, 5):
                media.append(types.InputMediaPhoto(data[i], f'Example {i}'))
            msg1_id = await bot.send_message(message.chat.id, DESIGN_STARTUP_TEXT, reply_markup=reply_keyboard)
            msg2_id = await bot.send_media_group(message.chat.id, media)
            if in_favorite:
                markup = 'favorite_keyboard'
                msg3_id = await bot.send_message(message.chat.id, DESIGN_DESCRIPTION_TEXT.format(data[5], data[6]),
                                                 reply_markup=favorite_keyboard)
            else:
                markup = 'design_keyboard'
                msg3_id = await bot.send_message(message.chat.id, DESIGN_DESCRIPTION_TEXT.format(data[5], data[6]),
                                                 reply_markup=design_keyboard)
            s.execute(
                update(User).where(User.user_id == message.from_user.id).values(last_keyboard=markup)
            )
            s.commit()
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
            s.commit()

        # Set overview to True
        s.execute(update(User).filter(User.user_id == message.from_user.id).values(check_image_overview=0))
        s.commit()

        # Handler defaults
        await reply_handler_set_defaults(s, message, 0, COMPLEX_DESIGN_COMMAND)

        # Delete old messages
        await bot.delete_message(message.chat.id, message.message_id)
        await delete_old_messages(s, old_messages)
    except Exception as e:
        # print('reply complex exc: ', e)
        await bot.delete_message(message.chat.id, message.message_id)
    finally:
        if message.from_user.id in users_set:
            users_set.remove(message.from_user.id)
        s.close()


@dp.message_handler(lambda message: message.text == FAVORITE_COMMAND)
async def reply_favorite_command_handler(message: types.Message):
    s = DBSession()
    try:
        if message.from_user.id in users_set:
            await bot.delete_message(message.chat.id, message.message_id)
            return
        else:
            users_set.add(message.from_user.id)

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
            s.commit()
            s.execute(
                insert(Message).values(
                    [
                        {'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(msg1_id)},
                        *[{'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(elem)} for
                          elem in msg2_id],
                        {'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(msg3_id)}
                    ]
                )
            )
            s.commit()
        else:
            msg_id = await bot.send_message(message.chat.id, NO_FAVORITE_MESSAGE_TEXT, reply_markup=reply_keyboard)
            s.execute(
                insert(Message).values(
                    user_id=message.from_user.id,
                    chat_id=message.chat.id,
                    message_id=int(msg_id)
                )
            )
            s.commit()

        # Set overview to True
        s.execute(update(User).filter(User.user_id == message.from_user.id).values(check_image_overview=0))
        s.commit()

        # Handler defaults
        await reply_handler_set_defaults(s, message, 0, FAVORITE_COMMAND)

        # Delete old messages
        await bot.delete_message(message.chat.id, message.message_id)
        await delete_old_messages(s, old_messages)
    except Exception as e:
        # print('reply fav exc: ', e)
        await bot.delete_message(message.chat.id, message.message_id)
    finally:
        if message.from_user.id in users_set:
            users_set.remove(message.from_user.id)
        s.close()


@dp.message_handler(lambda message: message.text == HELP_COMMAND)
async def reply_help_command_handler(message: types.Message):
    s = DBSession()
    try:
        if message.from_user.id in users_set:
            await bot.delete_message(message.chat.id, message.message_id)
            return
        else:
            users_set.add(message.from_user.id)

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
            s.commit()
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
            s.commit()

        # Set overview to True
        s.execute(update(User).filter(User.user_id == message.from_user.id).values(check_image_overview=0))
        s.commit()

        # Handler defaults
        await reply_handler_set_defaults(s, message, 0, HELP_COMMAND)

        # Delete old messages
        await bot.delete_message(message.chat.id, message.message_id)
        await delete_old_messages(s, old_messages)
    except Exception as e:
        # print('reply help exc: ', e)
        await bot.delete_message(message.chat.id, message.message_id)
    finally:
        if message.from_user.id in users_set:
            users_set.remove(message.from_user.id)
        s.close()


@dp.message_handler(lambda message: message.text == EXAMPLES_COMMAND)
async def reply_examples_command_handler(message: types.Message):
    s = DBSession()
    try:
        if message.from_user.id in users_set:
            await bot.delete_message(message.chat.id, message.message_id)
            return
        else:
            users_set.add(message.from_user.id)

        # Get actual messages
        old_messages = await get_actual_message(s, message.from_user.id)

        # Loading images from resources
        data, _ = await ResourceLoader.load_images(ResourceType.Example)

        # Display messages and update message_id in Message table
        if data is not None and len(data) > 0:
            media = list()
            media.append(types.InputMediaPhoto(data[0]))
            msg1_id = await bot.send_message(message.chat.id, EXAMPLES_MESSAGE_TEXT, reply_markup=reply_keyboard)
            msg2_id = await bot.send_media_group(message.chat.id, media)
            msg3_id = await bot.send_message(message.chat.id, f'Пример работы', reply_markup=help_keyboard)
            s.execute(
                update(User).where(User.user_id == message.from_user.id).values(last_keyboard='help_keyboard')
            )
            s.commit()
            s.execute(
                insert(Message).values(
                    [
                        {'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(msg1_id)},
                        {'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(msg2_id[0])},
                        {'user_id': message.from_user.id, 'chat_id': message.chat.id, 'message_id': int(msg3_id)}
                    ]
                )
            )
            s.commit()

        # Set overview to True
        s.execute(update(User).filter(User.user_id == message.from_user.id).values(check_image_overview=0))
        s.commit()

        # Handler defaults
        await reply_handler_set_defaults(s, message, 0, EXAMPLES_COMMAND)

        # Delete old messages
        await bot.delete_message(message.chat.id, message.message_id)
        await delete_old_messages(s, old_messages)
    except Exception as e:
        # print('reply example exc: ', e)
        await bot.delete_message(message.chat.id, message.message_id)
    finally:
        if message.from_user.id in users_set:
            users_set.remove(message.from_user.id)
        s.close()
