from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from prisma.enums import Team

from src.utils.get_back_to_menu_button import get_back_to_menu_button


def get_teams_keyboard(prefix: str):
    keyboard = []

    for team in Team:
        if team.value == "NO_TEAM":
            continue

        keyboard.append([InlineKeyboardButton(
            team.name.replace("_", " ").capitalize(), callback_data=f"{prefix} {team.value}")])

    keyboard.append(
        [get_back_to_menu_button("❌ " + "کنسل")]
    )

    return InlineKeyboardMarkup(keyboard)
