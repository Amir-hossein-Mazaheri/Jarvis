from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from prisma.enums import Team

from src.utils.get_back_to_menu_button import get_back_to_menu_button


def get_teams_keyboard(prefix: str, include_cancel_button=True, return_keyboard=True):
    keyboard_buttons = []

    for team in Team:
        if team.value == "NO_TEAM":
            continue

        keyboard_buttons.append([InlineKeyboardButton(
            team.name.replace("_", " ").capitalize(), callback_data=f"{prefix} {team.value}")])

    if include_cancel_button:
        keyboard_buttons.append(
            [get_back_to_menu_button("❌ " + "کنسل")]
        )

    if return_keyboard:
        return InlineKeyboardMarkup(keyboard_buttons)

    return keyboard_buttons
