from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from aiogram_bot.commands.reply_commands import (
    SIMPLE_DESIGN_COMMAND,
    COMPLEX_DESIGN_COMMAND,
    FAVORITE_COMMAND,
    HELP_COMMAND
)


simple_design_button = KeyboardButton(SIMPLE_DESIGN_COMMAND)
complex_design_button = KeyboardButton(COMPLEX_DESIGN_COMMAND)
favorite_button = KeyboardButton(FAVORITE_COMMAND)
help_button = KeyboardButton(HELP_COMMAND)
reply_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True
).add(simple_design_button, complex_design_button).add(favorite_button, help_button)
