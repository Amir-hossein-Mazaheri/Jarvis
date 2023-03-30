from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.utils.get_back_to_menu_button import get_back_to_menu_button
from src.constants.commands import BACK_TO_HEAD_ACTIONS


def get_head_common_keyboard(prev_menu_callback: str = None, prev_menu_text: str = None, return_keyboard=True, for_admin=False):
    keyboard_buttons = [
        [InlineKeyboardButton(
            "بازگشت به لیست کارای ادمینی", callback_data=BACK_TO_ADMIN_ACTIONS)] if for_admin else [InlineKeyboardButton(
                "🎛️ " + "بازگشت به منوی کارای هدی", callback_data=BACK_TO_HEAD_ACTIONS)],
        [get_back_to_menu_button()]
    ]

    if prev_menu_callback:
        keyboard_buttons = [InlineKeyboardButton(
            prev_menu_text, callback_data=prev_menu_callback)] + keyboard_buttons

    if return_keyboard:
        return InlineKeyboardMarkup(keyboard_buttons)
    else:
        return keyboard_buttons
