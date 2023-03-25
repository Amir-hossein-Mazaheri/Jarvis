from enum import Enum
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes

from src.constants.commands import REGISTER, EDIT, QUESTIONS, STAT, QUESTIONS_HISTORY, SHOW_HELP
from src.utils.is_user_registered import is_user_registered
from src.utils.is_admin import is_admin
from src.constants.commands import ADMIN


class KeyboardActions(Enum):
    REGISTER = "REGISTER"
    QUIZ = "QUIZ"
    STAT = "STAT"
    HELP_AND_EDIT = "HELP_AND_EDIT"
    HISTORY = "HISTORY"
    ADMIN = "ADMIN"


async def get_actions_keyboard(update: Update, ctx: ContextTypes.DEFAULT_TYPE, exclude: list[KeyboardActions] = []):
    keyboard_actions = {
        KeyboardActions.REGISTER: [InlineKeyboardButton("➕ " + "ثبت نام", callback_data=REGISTER)],
        KeyboardActions.QUIZ: [InlineKeyboardButton("❓ " + "آزمون دادن", callback_data=QUESTIONS)],
        KeyboardActions.STAT: [InlineKeyboardButton("🏴 " + "دیدن وضعیت سوالایی که جواب دادی", callback_data=STAT)],
        KeyboardActions.HELP_AND_EDIT: [InlineKeyboardButton("ℹ️ " + "راهنما", callback_data=SHOW_HELP), InlineKeyboardButton("👤 " + "ویرایش اطلاعات", callback_data=EDIT)],
        KeyboardActions.HISTORY: [InlineKeyboardButton("📃 " + " سول آزمون هایی که تا حالا برگزار شده", callback_data=QUESTIONS_HISTORY)],
        KeyboardActions.ADMIN: [InlineKeyboardButton("🧑‍💼 " + "کارای ادمینی", callback_data=ADMIN)],
    }

    keyboard_buttons = []

    if not await is_user_registered(update, ctx):
        keyboard_buttons.append(keyboard_actions[KeyboardActions.REGISTER])
    else:
        for action in keyboard_actions:
            if action in exclude or action == KeyboardActions.REGISTER or action == KeyboardActions.ADMIN:
                continue

            keyboard_buttons.append(keyboard_actions[action])

        if await is_admin(update, ctx):
            keyboard_buttons.append(keyboard_actions[KeyboardActions.ADMIN])

    return InlineKeyboardMarkup(keyboard_buttons)
