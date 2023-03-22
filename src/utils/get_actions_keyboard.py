from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes

from src.constants.commands import REGISTER, EDIT, QUESTIONS, STAT, QUESTIONS_HISTORY
from src.utils.is_user_registered import is_user_registered


async def get_actions_keyboard(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    keyboard_buttons = []

    if not await is_user_registered(user_id):
        keyboard_buttons.append(
            [InlineKeyboardButton("Register", callback_data=REGISTER)])
    else:
        keyboard_buttons = [
            [InlineKeyboardButton("Questions Exam", callback_data=QUESTIONS)],
            [InlineKeyboardButton(
                "See What you have done till now", callback_data=STAT)],
            [InlineKeyboardButton("History of questions that been held", callback_data=QUESTIONS_HISTORY), InlineKeyboardButton(
                "Edit your student code or nickname", callback_data=EDIT)]
        ]

    return InlineKeyboardMarkup(keyboard_buttons)
