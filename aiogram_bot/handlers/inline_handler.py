from aiogram import types
import json
from sqlalchemy import insert, update, delete, and_

from aiogram_bot.keyboards.reply_keyboard import reply_keyboard
from aiogram_bot.handlers.utils import delete_old_messages, get_actual_message

from aiogram_bot.models.user import User
from aiogram_bot.models.message import Message
from aiogram_bot.models.user_favorites import UserFavorites

from aiogram_bot.misc.resources_loader import ResourceType, ResourceLoader
from aiogram_bot.misc.db_connection import session_scope
from aiogram_bot.misc.bot_connection import dp, bot

from aiogram_bot.keyboards.inline_keyboard import (
    design_keyboard,
    design_view_keyboard,
    design_to_start_keyboard,
    favorite_keyboard,
    favorite_view_keyboard,
    favorite_to_start_keyboard,
    help_keyboard,
    help_to_start_keyboard,
    help_view_keyboard,
    overview_keyboard,
    instruction_keyboard,
    keyboards_dict
)

from aiogram_bot.commands.reply_commands import (
    SIMPLE_DESIGN_COMMAND,
    COMPLEX_DESIGN_COMMAND,
    FAVORITE_COMMAND,
    HELP_COMMAND
)
from aiogram_bot.commands.inline_commands import (
    OVERVIEW_DESIGN_COMMAND,
    ORDER_COMMAND,
    TO_FAVORITE_COMMAND,
    NEXT_DESIGN_COMMAND,
    NEXT_COMMAND,
    PREV_COMMAND,
    TO_START_COMMAND,
    DELETE_COMMAND,
    NEXT_SCENARIO_COMMAND,
    ORDER_DESIGN_COMMAND,
    RETURN_COMMAND,
    INSTRUCTION_COMMAND,
    UPLOAD_NEW_IMAGE_COMMAND
)
from aiogram_bot.commands.text_commands import (
    NO_FAVORITE_MESSAGE,
    OVERVIEW_STARTUP_TEXT,
    OVERVIEW_LOAD_PHOTO_TEXT,
    DESIGN_STARTUP_TEXT,
    DESIGN_DESCRIPTION_TEXT,
    INSTRUCTION_TEXT,
    UPLOAD_PHOTO_TEXT,
    HELP_DESCRIPTION_TEXT
)


@dp.callback_query_handler(lambda c: c.data and c.data == UPLOAD_NEW_IMAGE_COMMAND)
async def inline_upload_new_image_command_handler(callback_query: types.CallbackQuery):
    with session_scope() as s:
        msg_id = await bot.send_message(callback_query.message.chat.id, UPLOAD_PHOTO_TEXT, reply_markup=reply_keyboard)
        s.execute(
            insert(Message).values(
                user_id=callback_query.from_user.id,
                chat_id=callback_query.message.chat.id,
                message_id=int(msg_id)
            )
        )


@dp.callback_query_handler(lambda c: c.data and c.data == INSTRUCTION_COMMAND)
async def inline_instruction_command_handler(callback_query: types.CallbackQuery):
    with session_scope() as s:
        # Get old messages
        old_messages = await get_actual_message(s, callback_query.from_user.id)

        # Write instruction messages
        msg_id = await bot.send_message(
            callback_query.message.chat.id, INSTRUCTION_TEXT, reply_markup=instruction_keyboard)
        s.execute(
            insert(Message).values(
                user_id=callback_query.from_user.id,
                chat_id=callback_query.message.chat.id,
                message_id=int(msg_id)
            )
        )

        # Delete old messages
        await delete_old_messages(s, old_messages)


@dp.callback_query_handler(lambda c: c.data and c.data == OVERVIEW_DESIGN_COMMAND)
async def inline_overview_design_command_handler(callback_query: types.CallbackQuery):
    with session_scope() as s:
        # Set overview to True
        s.execute(update(User).filter(User.user_id == callback_query.from_user.id).values(check_image_overview=1))

        # Get old messages
        old_messages = await get_actual_message(s, callback_query.from_user.id)

        # Write startup message
        msg1_id = await bot.send_message(
            callback_query.message.chat.id, OVERVIEW_STARTUP_TEXT, reply_markup=reply_keyboard)
        msg2_id = await bot.send_message(
            callback_query.message.chat.id, OVERVIEW_LOAD_PHOTO_TEXT, reply_markup=overview_keyboard)
        s.execute(insert(Message).values(
                [
                    {'user_id': callback_query.from_user.id,
                     'chat_id': callback_query.message.chat.id,
                     'message_id': int(msg1_id)},
                    {'user_id': callback_query.from_user.id,
                     'chat_id': callback_query.message.chat.id,
                     'message_id': int(msg2_id)},
                ]
            )
        )

        # Delete old messages
        # await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
        await delete_old_messages(s, old_messages)


@dp.callback_query_handler(lambda c: c.data and (c.data == ORDER_COMMAND or c.data == ORDER_DESIGN_COMMAND))
async def inline_order_command_handler(callback_query: types.CallbackQuery):
    pass


@dp.callback_query_handler(lambda c: c.data and c.data == RETURN_COMMAND)
async def inline_return_command_handler(callback_query: types.CallbackQuery):
    with session_scope() as s:
        # Set overview to True
        s.execute(update(User).filter(User.user_id == callback_query.from_user.id).values(check_image_overview=0))

        # Get user last_index
        user_request = s.query(User).filter(User.user_id == callback_query.from_user.id).first()
        if user_request is None:
            return

        # Get old messages
        old_messages = await get_actual_message(s, callback_query.from_user.id)

        # Get data using ResourceLoader
        data = None
        last_reply_command = user_request.last_reply_command
        if last_reply_command == SIMPLE_DESIGN_COMMAND:
            data, _ = await ResourceLoader.load_images(ResourceType.Simple, user_request.last_index)
        elif last_reply_command == COMPLEX_DESIGN_COMMAND:
            data, _ = await ResourceLoader.load_images(ResourceType.Complex, user_request.last_index)
        elif last_reply_command == FAVORITE_COMMAND:
            data, _ = await ResourceLoader.load_favorites(callback_query.from_user.id, user_request.last_index)
        if data is None:
            return

        # Display messages and update message_id in Message table
        if data is not None and len(data) > 0:
            media = list()
            for i in range(1, 5):
                media.append(types.InputMediaPhoto(data[i], f'Example {i}'))

            msg1_id = await bot.send_message(callback_query.message.chat.id, DESIGN_STARTUP_TEXT, reply_markup=reply_keyboard)
            msg2_id = await bot.send_media_group(callback_query.message.chat.id, media)
            msg3_id = await bot.send_message(
                callback_query.message.chat.id, DESIGN_DESCRIPTION_TEXT.format(data[5], data[6]),
                reply_markup=keyboards_dict[user_request.last_keyboard])

            s.execute(insert(Message).values(
                [
                    {'user_id': callback_query.from_user.id, 'chat_id': callback_query.message.chat.id, 'message_id': int(msg1_id)},
                    *[{'user_id': callback_query.from_user.id, 'chat_id': callback_query.message.chat.id, 'message_id': int(elem)}
                      for elem in msg2_id],
                    {'user_id': callback_query.from_user.id, 'chat_id': callback_query.message.chat.id, 'message_id': int(msg3_id)}
                ]
            ))

        # Delete old messages
        # await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
        await delete_old_messages(s, old_messages)


@dp.callback_query_handler(lambda c: c.data and c.data == TO_FAVORITE_COMMAND)
async def inline_to_favorite_command_handler(callback_query: types.CallbackQuery):
    with session_scope() as s:
        # Get user last_index
        user_request = s.query(User).filter(User.user_id == callback_query.from_user.id).first()
        if user_request is None:
            return

        # Get data using ResourceLoader
        data = None
        last_reply_command = user_request.last_reply_command
        if last_reply_command == SIMPLE_DESIGN_COMMAND:
            data, _ = await ResourceLoader.load_images(ResourceType.Simple, user_request.last_index)
        elif last_reply_command == COMPLEX_DESIGN_COMMAND:
            data, _ = await ResourceLoader.load_images(ResourceType.Complex, user_request.last_index)
        elif last_reply_command == FAVORITE_COMMAND:
            data, _ = await ResourceLoader.load_favorites(callback_query.from_user.id, user_request.last_index)
        if data is None:
            return

        # Adding row to User_favorites table
        resource_string = ','.join([elem.strip() for elem in data])
        request = s.query(UserFavorites).filter(
            and_(UserFavorites.user_id == callback_query.from_user.id, UserFavorites.resource == resource_string)
        ).first()
        if request is None:
            s.execute(
                insert(UserFavorites).values(
                    user_id=callback_query.from_user.id,
                    resource=resource_string,
                    resource_type=user_request.last_reply_command
                )
            )


@dp.callback_query_handler(
    lambda c: c.data and (c.data == NEXT_DESIGN_COMMAND or c.data == NEXT_COMMAND or c.data == NEXT_SCENARIO_COMMAND))
async def inline_next_design_command_handler(callback_query: types.CallbackQuery):
    with session_scope() as s:
        # Get user last_index
        user_request = s.query(User).filter(User.user_id == callback_query.from_user.id).first()
        if user_request is None:
            return

        # Get data using ResourceLoader
        try:
            last_index = user_request.last_index
            new_index = last_index + 1
            last_reply_command = user_request.last_reply_command
            data = None
            if last_reply_command == SIMPLE_DESIGN_COMMAND:
                data, is_last_index = await ResourceLoader.load_images(ResourceType.Simple, new_index)
            elif last_reply_command == COMPLEX_DESIGN_COMMAND:
                data, is_last_index = await ResourceLoader.load_images(ResourceType.Complex, new_index)
            elif last_reply_command == HELP_COMMAND:
                data, is_last_index = await ResourceLoader.load_images(ResourceType.Help, new_index)
            elif last_reply_command == FAVORITE_COMMAND:
                data, is_last_index = await ResourceLoader.load_favorites(callback_query.from_user.id, new_index)
            if data is None:
                return
        except:
            return

        # Update user last_index and image messages
        s.execute(update(User).where(User.user_id == callback_query.from_user.id).values(last_index=new_index))
        message_request = s.query(Message).filter(Message.user_id == callback_query.from_user.id).all()

        try:
            if last_reply_command == HELP_COMMAND:
                for i in range(2, 4):
                    await bot.edit_message_media(
                        types.InputMediaPhoto(data[i - 2], f'Example {i}'),
                        callback_query.message.chat.id, message_request[i].message_id)
                await bot.edit_message_text(HELP_DESCRIPTION_TEXT.format(data[2], data[3]),
                                            callback_query.message.chat.id, message_request[-1].message_id)
            else:
                for i in range(1, 5):
                    await bot.edit_message_media(
                        types.InputMediaPhoto(data[i], f'Example {i}'),
                        callback_query.message.chat.id, message_request[i].message_id)
                await bot.edit_message_text(DESIGN_DESCRIPTION_TEXT.format(data[5], data[6]),
                                            callback_query.message.chat.id, message_request[-1].message_id)
        except:
            pass

        # Updating keyboard
        try:
            if is_last_index is True:
                if last_reply_command == FAVORITE_COMMAND:
                    markup = favorite_to_start_keyboard
                    s.execute(
                        update(User).where(User.user_id == callback_query.from_user.id).values(
                            last_keyboard='favorite_to_start_keyboard')
                    )
                elif last_reply_command == HELP_COMMAND:
                    markup = help_to_start_keyboard
                    s.execute(
                        update(User).where(User.user_id == callback_query.from_user.id).values(
                            last_keyboard='help_to_start_keyboard')
                    )
                else:
                    markup = design_to_start_keyboard
                    s.execute(
                        update(User).where(User.user_id == callback_query.from_user.id).values(
                            last_keyboard='design_to_start_keyboard')
                    )
                await bot.edit_message_reply_markup(
                    callback_query.message.chat.id, message_request[-1].message_id, reply_markup=markup)
            else:
                if last_index == 0:
                    if last_reply_command == FAVORITE_COMMAND:
                        markup = favorite_view_keyboard
                        s.execute(
                            update(User).where(
                                User.user_id == callback_query.from_user.id).values(
                                last_keyboard='favorite_view_keyboard')
                        )
                    elif last_reply_command == HELP_COMMAND:
                        markup = help_view_keyboard
                        s.execute(
                            update(User).where(
                                User.user_id == callback_query.from_user.id).values(
                                last_keyboard='help_view_keyboard')
                        )
                    else:
                        markup = design_view_keyboard
                        s.execute(
                            update(User).where(
                                User.user_id == callback_query.from_user.id).values(
                                last_keyboard='design_view_keyboard')
                        )
                await bot.edit_message_reply_markup(
                    callback_query.message.chat.id, message_request[-1].message_id, reply_markup=markup)
        except:
            pass


@dp.callback_query_handler(lambda c: c.data and c.data == PREV_COMMAND)
async def inline_prev_design_command_handler(callback_query: types.CallbackQuery):
    with session_scope() as s:
        # Get user last_index
        user_request = s.query(User).filter(User.user_id == callback_query.from_user.id).first()
        if user_request is None:
            return

        # Get data using ResourceLoader
        last_index = user_request.last_index
        new_index = last_index - 1
        last_reply_command = user_request.last_reply_command
        data = None
        if last_reply_command == SIMPLE_DESIGN_COMMAND:
            data, _ = await ResourceLoader.load_images(ResourceType.Simple, new_index)
        elif last_reply_command == COMPLEX_DESIGN_COMMAND:
            data, _ = await ResourceLoader.load_images(ResourceType.Complex, new_index)
        elif last_reply_command == HELP_COMMAND:
            data, _ = await ResourceLoader.load_images(ResourceType.Help, new_index)
        elif last_reply_command == FAVORITE_COMMAND:
            data, _ = await ResourceLoader.load_favorites(callback_query.from_user.id, new_index)
        if data is None:
            return

        # Update user last_index and image messages
        s.execute(update(User).where(User.user_id == callback_query.from_user.id).values(last_index=new_index))
        message_request = s.query(Message).filter(Message.user_id == callback_query.from_user.id).all()

        try:
            if last_reply_command == HELP_COMMAND:
                for i in range(2, 4):
                    await bot.edit_message_media(
                        types.InputMediaPhoto(data[i - 2], f'Example {i}'),
                        callback_query.message.chat.id, message_request[i].message_id)
                await bot.edit_message_text(HELP_DESCRIPTION_TEXT.format(data[2], data[3]),
                                            callback_query.message.chat.id, message_request[-1].message_id)
            else:
                for i in range(1, 5):
                    await bot.edit_message_media(
                        types.InputMediaPhoto(data[i], f'Example {i}'),
                        callback_query.message.chat.id, message_request[i].message_id)
                await bot.edit_message_text(DESIGN_DESCRIPTION_TEXT.format(data[5], data[6]),
                    callback_query.message.chat.id, message_request[-1].message_id)
        except:
            pass

        # Updating keyboard
        try:
            if new_index == 0:
                if last_reply_command == FAVORITE_COMMAND:
                    markup = favorite_keyboard
                    s.execute(
                        update(User).where(User.user_id == callback_query.from_user.id).values(
                            last_keyboard='favorite_keyboard')
                    )
                elif last_reply_command == HELP_COMMAND:
                    markup = help_keyboard
                    s.execute(
                        update(User).where(User.user_id == callback_query.from_user.id).values(
                            last_keyboard='help_keyboard')
                    )
                else:
                    markup = design_keyboard
                    s.execute(
                        update(User).where(User.user_id == callback_query.from_user.id).values(
                            last_keyboard='design_keyboard')
                    )
                await bot.edit_message_reply_markup(
                    callback_query.message.chat.id, message_request[-1].message_id, reply_markup=markup)
            else:
                if last_reply_command == FAVORITE_COMMAND:
                    markup = favorite_view_keyboard
                    s.execute(
                        update(User).where(User.user_id == callback_query.from_user.id).values(
                            last_keyboard='favorite_view_keyboard')
                    )
                elif last_reply_command == HELP_COMMAND:
                    markup = help_view_keyboard
                    s.execute(
                        update(User).where(User.user_id == callback_query.from_user.id).values(
                            last_keyboard='help_view_keyboard')
                    )
                else:
                    markup = design_view_keyboard
                    s.execute(
                        update(User).where(User.user_id == callback_query.from_user.id).values(
                            last_keyboard='design_view_keyboard')
                    )
                await bot.edit_message_reply_markup(
                    callback_query.message.chat.id, message_request[-1].message_id, reply_markup=markup)
        except:
            pass


@dp.callback_query_handler(lambda c: c.data and c.data == TO_START_COMMAND)
async def inline_to_start_command_handler(callback_query: types.CallbackQuery):
    with session_scope() as s:
        # Get user last_index
        user_request = s.query(User).filter(User.user_id == callback_query.from_user.id).first()
        if user_request is None:
            return

        # Get data using ResourceLoader
        last_reply_command = user_request.last_reply_command
        data = None
        if last_reply_command == SIMPLE_DESIGN_COMMAND:
            data, _ = await ResourceLoader.load_images(ResourceType.Simple)
        elif last_reply_command == COMPLEX_DESIGN_COMMAND:
            data, _ = await ResourceLoader.load_images(ResourceType.Complex)
        elif last_reply_command == HELP_COMMAND:
            data, _ = await ResourceLoader.load_images(ResourceType.Help)
        elif last_reply_command == FAVORITE_COMMAND:
            data, _ = await ResourceLoader.load_favorites(callback_query.from_user.id)
        if data is None:
            return

        # Update user last_index and image messages
        s.execute(update(User).where(User.user_id == callback_query.from_user.id).values(last_index=0))
        message_request = s.query(Message).filter(Message.user_id == callback_query.from_user.id).all()

        try:
            if last_reply_command == HELP_COMMAND:
                for i in range(2, 4):
                    await bot.edit_message_media(
                        types.InputMediaPhoto(data[i - 2], f'Example {i}'),
                        callback_query.message.chat.id, message_request[i].message_id)
                await bot.edit_message_text(HELP_DESCRIPTION_TEXT.format(data[2], data[3]),
                                            callback_query.message.chat.id, message_request[-1].message_id)
            else:
                for i in range(1, 5):
                    await bot.edit_message_media(
                        types.InputMediaPhoto(data[i], f'Example {i}'),
                        callback_query.message.chat.id, message_request[i].message_id)
                await bot.edit_message_text(DESIGN_DESCRIPTION_TEXT.format(data[5], data[6]),
                                            callback_query.message.chat.id, message_request[-1].message_id)
        except:
            pass

        # Edit keyboard
        try:
            if last_reply_command == FAVORITE_COMMAND:
                markup = favorite_keyboard
                s.execute(
                    update(User).where(User.user_id == callback_query.from_user.id).values(
                        last_keyboard='favorite_keyboard')
                )
            elif last_reply_command == HELP_COMMAND:
                markup = help_keyboard
                s.execute(
                    update(User).where(User.user_id == callback_query.from_user.id).values(
                        last_keyboard='help_keyboard')
                )
            else:
                markup = design_keyboard
                s.execute(
                    update(User).where(User.user_id == callback_query.from_user.id).values(
                        last_keyboard='design_keyboard')
                )
            await bot.edit_message_reply_markup(
                callback_query.message.chat.id, message_request[-1].message_id, reply_markup=markup
            )
        except:
            pass


@dp.callback_query_handler(lambda c: c.data and c.data == DELETE_COMMAND)
async def inline_delete_command_handler(callback_query: types.CallbackQuery):
    with session_scope() as s:
        # Get user last_index
        user_request = s.query(User).filter(User.user_id == callback_query.from_user.id).first()
        if user_request is None:
            return

        # Get data using ResourceLoader
        last_index = user_request.last_index
        data, is_last_index = await ResourceLoader.load_favorites(callback_query.from_user.id, last_index)
        if data is None:
            return

        # Delete favorite resource
        resource_string = ','.join([elem.strip() for elem in data])
        s.execute(
            delete(UserFavorites).where(and_(UserFavorites.user_id == callback_query.from_user.id,
                                             UserFavorites.resource == resource_string))
        )

        # Move last_index
        if is_last_index is True:
            if last_index == 0:
                message_request = s.query(Message).filter(Message.user_id == callback_query.from_user.id).all()
                for result in message_request:
                    await bot.delete_message(callback_query.message.chat.id, result.message_id)
                s.execute(delete(Message).where(Message.user_id == callback_query.from_user.id))

                msg_id = await bot.send_message(
                    callback_query.message.chat.id, NO_FAVORITE_MESSAGE,
                    reply_markup=reply_keyboard)
                s.execute(
                    insert(Message).values(
                        user_id=callback_query.from_user.id,
                        chat_id=callback_query.message.chat.id,
                        message_id=int(msg_id)
                    )
                )
            else:
                s.commit()
                await inline_to_start_command_handler(callback_query)
        else:
            s.commit()
            await inline_to_start_command_handler(callback_query)
