from aiogram import types
from sqlalchemy import insert, update, and_

from aiogram_bot.models.user import User
from aiogram_bot.models.message import Message
from aiogram_bot.models.user_favorites import UserFavorites

from aiogram_bot.misc.resources_loader import ResourceType, ResourceLoader
from aiogram_bot.misc.db_connection import session_scope
from aiogram_bot.misc.bot_connection import dp, bot

from aiogram_bot.keyboards.inline_keyboard import (
    inline_main_design_keyboard,
    inline_overview_design_keyboard,
    inline_to_start_design_keyboard,
    inline_favorite_main_design_keyboard,
    inline_favorite_overview_design_keyboard,
    inline_favorite_to_start_design_keyboard
)

from aiogram_bot.config.reply_commands import (
    SIMPLE_DESIGN_COMMAND,
    COMPLEX_DESIGN_COMMAND,
    FAVORITE_COMMAND,
    HELP_COMMAND
)
from aiogram_bot.config.inline_commands import (
    OVERVIEW_DESIGN_COMMAND,
    ORDER_COMMAND,
    TO_FAVORITE_COMMAND,
    NEXT_DESIGN_COMMAND,
    NEXT_COMMAND,
    PREV_COMMAND,
    TO_START_COMMAND,
    DELETE_COMMAND,
)
from aiogram_bot.config.text_defines import (
    DESIGN_DESCRIPTION_TEXT
)


@dp.callback_query_handler(lambda c: c.data and c.data == OVERVIEW_DESIGN_COMMAND)
async def inline_overview_design_command_handler(callback_query: types.CallbackQuery):
    pass


@dp.callback_query_handler(lambda c: c.data and c.data == ORDER_COMMAND)
async def inline_order_command_handler(callback_query: types.CallbackQuery):
    pass


@dp.callback_query_handler(lambda c: c.data and c.data == TO_FAVORITE_COMMAND)
async def inline_to_favorite_command_handler(callback_query: types.CallbackQuery):
    with session_scope() as s:
        # Get last_index
        request = s.query(User).filter(User.user_id == callback_query.from_user.id).first()
        if request is None:
            return

        # Get data by given index
        try:
            # Check if bot can get images by given index
            if request.last_reply_command == SIMPLE_DESIGN_COMMAND:
                data = await ResourceLoader.load_resources(ResourceType.Simple, resource_index=request.last_index)
            elif request.last_reply_command == COMPLEX_DESIGN_COMMAND:
                data = await ResourceLoader.load_resources(ResourceType.Complex, resource_index=request.last_index)
        except:
            return

        # Adding row to User_favorites table
        resource_string = ','.join([elem.strip() for elem in data])
        request = s.query(UserFavorites).filter(
            and_(UserFavorites.user_id == callback_query.from_user.id, UserFavorites.resource == resource_string)
        ).first()
        if request is None:
            request = insert(UserFavorites).values(
                user_id=callback_query.from_user.id,
                resource=resource_string
            )
            s.execute(request)


@dp.callback_query_handler(lambda c: c.data and (c.data == NEXT_DESIGN_COMMAND or c.data == NEXT_COMMAND))
async def inline_next_design_command_handler(callback_query: types.CallbackQuery):
    with session_scope() as s:
        # Get last index of user
        request = s.query(User).filter(User.user_id == callback_query.from_user.id).first()
        if request is None:
            return

        last_index = request.last_index
        last_reply_command = request.last_reply_command
        try:
            # Check if bot can get images by given index
            if last_reply_command == SIMPLE_DESIGN_COMMAND:
                data = await ResourceLoader.load_resources(ResourceType.Simple, resource_index=last_index + 1)
            elif last_reply_command == COMPLEX_DESIGN_COMMAND:
                data = await ResourceLoader.load_resources(ResourceType.Complex, resource_index=last_index + 1)
            elif last_reply_command == FAVORITE_COMMAND:
                data = await ResourceLoader.load_favorites(callback_query.from_user.id, resource_index=request.last_index + 1)
                print(data)
        except Exception as e:
            print('EXCEPTION: ', e)
            # Changing inline keyboard to 'To start inline keyboard'
            request = s.query(Message).filter(Message.user_id == callback_query.from_user.id).all()
            if last_reply_command == FAVORITE_COMMAND:
                await bot.edit_message_reply_markup(
                    callback_query.message.chat.id, request[-1].message_id, reply_markup=inline_favorite_to_start_design_keyboard)
            else:
                await bot.edit_message_reply_markup(
                    callback_query.message.chat.id, request[-1].message_id, reply_markup=inline_to_start_design_keyboard)
            return

        # Updating last_index of user and media message
        try:
            request = update(User).where(User.user_id == callback_query.from_user.id).values(last_index=last_index + 1)
            s.execute(request)

            request = s.query(Message).filter(Message.user_id == callback_query.from_user.id)
            for i in range(1, 5):
                await bot.edit_message_media(types.InputMediaPhoto(data[i], f'Example {i}'), callback_query.message.chat.id,
                                             request[i].message_id)
        except:
            return

        # Changing keyboard if needed
        try:
            if last_index + 1 > 0:
                if last_reply_command == FAVORITE_COMMAND:
                    await bot.edit_message_reply_markup(
                        callback_query.message.chat.id, request[-1].message_id, reply_markup=inline_favorite_overview_design_keyboard)
                else:
                    await bot.edit_message_reply_markup(
                        callback_query.message.chat.id, request[-1].message_id, reply_markup=inline_overview_design_keyboard)
        except:
            if last_reply_command == FAVORITE_COMMAND:
                await bot.edit_message_reply_markup(
                    callback_query.message.chat.id, request[-1].message_id, reply_markup=inline_favorite_to_start_design_keyboard)
            else:
                await bot.edit_message_reply_markup(
                    callback_query.message.chat.id, request[-1].message_id, reply_markup=inline_to_start_design_keyboard)


@dp.callback_query_handler(lambda c: c.data and c.data == PREV_COMMAND)
async def inline_prev_design_command_handler(callback_query: types.CallbackQuery):
    with session_scope() as s:
        # Get last index of user
        request = s.query(User).filter(User.user_id == callback_query.from_user.id).first()
        if request is None:
            return

        last_index = request.last_index
        last_reply_command = request.last_reply_command
        try:
            # Check if bot can get images by given index
            if last_reply_command == SIMPLE_DESIGN_COMMAND:
                data = await ResourceLoader.load_resources(ResourceType.Simple, resource_index=last_index - 1)
            elif last_reply_command == COMPLEX_DESIGN_COMMAND:
                data = await ResourceLoader.load_resources(ResourceType.Complex, resource_index=last_index - 1)
            elif last_reply_command == FAVORITE_COMMAND:
                data = await ResourceLoader.load_favorites(callback_query.from_user.id, resource_index=request.last_index - 1)
        except Exception as e:
            # Changing inline keyboard to 'To start inline keyboard'
            request = s.query(Message).filter(Message.user_id == callback_query.from_user.id).all()
            if last_reply_command == FAVORITE_COMMAND:
                await bot.edit_message_reply_markup(
                    callback_query.message.chat.id, request[-1].message_id, reply_markup=inline_favorite_main_design_keyboard)
            else:
                await bot.edit_message_reply_markup(
                    callback_query.message.chat.id, request[-1].message_id, reply_markup=inline_main_design_keyboard)
            return

        # Updating last_index of user and media message
        try:
            request = update(User).where(User.user_id == callback_query.from_user.id).values(last_index=last_index - 1)
            s.execute(request)

            request = s.query(Message).filter(Message.user_id == callback_query.from_user.id)
            for i in range(1, 5):
                await bot.edit_message_media(types.InputMediaPhoto(data[i], f'Example {i}'),
                                             callback_query.message.chat.id,
                                             request[i].message_id)
        except:
            return

        # Changing keyboard if needed
        if last_index - 1 == 0:
            if last_reply_command == FAVORITE_COMMAND:
                await bot.edit_message_reply_markup(
                    callback_query.message.chat.id, request[-1].message_id, reply_markup=inline_favorite_main_design_keyboard)
            else:
                await bot.edit_message_reply_markup(
                    callback_query.message.chat.id, request[-1].message_id, reply_markup=inline_main_design_keyboard)
        else:
            if last_reply_command == FAVORITE_COMMAND:
                await bot.edit_message_reply_markup(
                    callback_query.message.chat.id, request[-1].message_id, reply_markup=inline_favorite_overview_design_keyboard)
            else:
                await bot.edit_message_reply_markup(
                    callback_query.message.chat.id, request[-1].message_id, reply_markup=inline_overview_design_keyboard)


@dp.callback_query_handler(lambda c: c.data and c.data == TO_START_COMMAND)
async def inline_to_start_command_handler(callback_query: types.CallbackQuery):
    with session_scope() as s:
        # Get last index of user
        request = s.query(User).filter(User.user_id == callback_query.from_user.id).first()
        if request is None:
            return

        try:
            # Check if bot can get images by given index
            if request.last_reply_command == SIMPLE_DESIGN_COMMAND:
                data = await ResourceLoader.load_resources(ResourceType.Simple, resource_index=0)
            elif request.last_reply_command == COMPLEX_DESIGN_COMMAND:
                data = await ResourceLoader.load_resources(ResourceType.Complex, resource_index=0)
            elif request.last_reply_command == FAVORITE_COMMAND:
                data = await ResourceLoader.load_favorites(callback_query.from_user.id, resource_index=0)
        except:
            return

        # Updating last_index of user and media message
        request = update(User).where(User.user_id == callback_query.from_user.id).values(last_index=0)
        s.execute(request)

        request = s.query(Message).filter(Message.user_id == callback_query.from_user.id)
        for i in range(1, 5):
            await bot.edit_message_media(types.InputMediaPhoto(data[i], f'Example {i}'),
                                         callback_query.message.chat.id,
                                         request[i].message_id)
        await bot.edit_message_reply_markup(callback_query.message.chat.id, request[-1].message_id,
                                            reply_markup=inline_main_design_keyboard)


@dp.callback_query_handler(lambda c: c.data and c.data == DELETE_COMMAND)
async def inline_delete_command_handler(callback_query: types.CallbackQuery):
    pass
