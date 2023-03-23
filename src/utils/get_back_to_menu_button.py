from telegram import InlineKeyboardButton

from src.constants.commands import BACK_TO_MENU


def get_back_to_menu_button(text="🔙 بازگشت به منو"):
    return InlineKeyboardButton(text, callback_data=BACK_TO_MENU)
