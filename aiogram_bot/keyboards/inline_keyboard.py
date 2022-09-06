from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from aiogram_bot.config.text_defines import (
    INLINE_OVERVIEW_BUTTON_TEXT,
    INLINE_ORDER_BUTTON_TEXT,
    INLINE_TO_FAVORITE_BUTTON_TEXT,
    INLINE_NEXT_DESIGN_BUTTON_TEXT,
    INLINE_NEXT_BUTTON_TEXT,
    INLINE_PREV_BUTTON_TEXT,
    INLINE_TO_START_BUTTON_TEXT,
    INLINE_DELETE_BUTTON_TEXT,
    INLINE_ORDER_DESIGN_BUTTON_TEXT,
    INLINE_NEXT_SCENARIO_BUTTON_TEXT
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
    ORDER_DESIGN_COMMAND,
    NEXT_SCENARIO_COMMAND
)


# Buttons
overview_button = InlineKeyboardButton(INLINE_OVERVIEW_BUTTON_TEXT, callback_data=OVERVIEW_DESIGN_COMMAND)
order_button = InlineKeyboardButton(INLINE_ORDER_BUTTON_TEXT, callback_data=ORDER_COMMAND)
to_favorite_button = InlineKeyboardButton(INLINE_TO_FAVORITE_BUTTON_TEXT, callback_data=TO_FAVORITE_COMMAND)
next_design_button = InlineKeyboardButton(INLINE_NEXT_DESIGN_BUTTON_TEXT, callback_data=NEXT_DESIGN_COMMAND)
next_button = InlineKeyboardButton(INLINE_NEXT_BUTTON_TEXT, callback_data=NEXT_COMMAND)
prev_button = InlineKeyboardButton(INLINE_PREV_BUTTON_TEXT, callback_data=PREV_COMMAND)
to_start_button = InlineKeyboardButton(INLINE_TO_START_BUTTON_TEXT, callback_data=TO_START_COMMAND)
delete_button = InlineKeyboardButton(INLINE_DELETE_BUTTON_TEXT, callback_data=DELETE_COMMAND)
order_design_button = InlineKeyboardButton(INLINE_ORDER_DESIGN_BUTTON_TEXT, callback_data=ORDER_DESIGN_COMMAND)
next_scenario_button = InlineKeyboardButton(INLINE_NEXT_SCENARIO_BUTTON_TEXT, callback_data=NEXT_SCENARIO_COMMAND)


# --- MAIN ---
# Main design template keyboard
design_keyboard = InlineKeyboardMarkup(row_width=2)
design_keyboard.add(overview_button)
design_keyboard.add(order_button, to_favorite_button, next_design_button)

# Overview design template keyboard
design_view_keyboard = InlineKeyboardMarkup(row_width=2)
design_view_keyboard.add(overview_button)
design_view_keyboard.add(order_button, to_favorite_button)
design_view_keyboard.add(prev_button, next_button)

# To start design template keyboard
design_to_start_keyboard = InlineKeyboardMarkup(row_width=2)
design_to_start_keyboard.add(overview_button)
design_to_start_keyboard.add(order_button, to_favorite_button)
design_to_start_keyboard.add(prev_button, to_start_button)


# --- FAVORITE ---
# Main favorite template keyboard
favorite_keyboard = InlineKeyboardMarkup(row_width=2)
favorite_keyboard.add(overview_button)
favorite_keyboard.add(order_button, delete_button, next_design_button)

# Overview favorite template keyboard
favorite_view_keyboard = InlineKeyboardMarkup(row_width=2)
favorite_view_keyboard.add(overview_button)
favorite_view_keyboard.add(order_button, delete_button)
favorite_view_keyboard.add(prev_button, next_button)

# To start favorite template keyboard
favorite_to_start_keyboard = InlineKeyboardMarkup(row_width=2)
favorite_to_start_keyboard.add(overview_button)
favorite_to_start_keyboard.add(order_button, delete_button)
favorite_to_start_keyboard.add(prev_button, to_start_button)


# --- HELP ---
help_keyboard = InlineKeyboardMarkup(row_width=2)
help_keyboard.add(order_design_button)
help_keyboard.add(next_scenario_button)

# Overview favorite template keyboard
help_view_keyboard = InlineKeyboardMarkup(row_width=2)
help_view_keyboard.add(order_design_button)
help_view_keyboard.add(prev_button, next_button)

# To start favorite template keyboard
help_to_start_keyboard = InlineKeyboardMarkup(row_width=2)
help_to_start_keyboard.add(order_design_button)
help_to_start_keyboard.add(prev_button, to_start_button)