from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes

from src.constants.commands import REGISTER, EDIT, QUESTIONS, STAT, QUESTIONS_HISTORY, SHOW_HELP
from src.utils.is_user_registered import is_user_registered
from src.utils.is_admin import is_admin
from src.constants.commands import ADMIN


async def get_actions_keyboard(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    keyboard_buttons = []

    if not await is_user_registered(update, ctx):
        keyboard_buttons.append(
            [InlineKeyboardButton("➕ " + "ثبت نام", callback_data=REGISTER)])
    else:
        keyboard_buttons = [
            [InlineKeyboardButton("❓ " + "آزمون دادن",
                                  callback_data=QUESTIONS)],
            [InlineKeyboardButton(
                "🏴 " + "دیدن وضعیت سوالایی که جواب دادی", callback_data=STAT)],
            [InlineKeyboardButton("ℹ️ " + "راهنما", callback_data=SHOW_HELP), InlineKeyboardButton(
                "👤 " + "ویرایش اطلاعات", callback_data=EDIT)],
            [InlineKeyboardButton(
                "📃 " + " سول آزمون هایی که تا حالا برگزار شده", callback_data=QUESTIONS_HISTORY)]
        ]

        if await is_admin(update, ctx):
            keyboard_buttons.append([InlineKeyboardButton(
                "🧑‍💼 " + "کارای ادمینی", callback_data=ADMIN)])

    return InlineKeyboardMarkup(keyboard_buttons)
