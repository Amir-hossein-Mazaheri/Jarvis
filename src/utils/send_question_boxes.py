from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime

from src.utils.db import db
from src.utils.send_message import send_message
from src.utils.get_back_to_menu_button import get_back_to_menu_button
from src.constants.commands import BACK_TO_ADMIN_ACTIONS, BACK_TO_HEAD_ACTIONS


async def send_question_boxes(update: Update, ctx: ContextTypes.DEFAULT_TYPE, for_admin: bool, prefix: str, title: str):
    user_id = update.effective_user.id
    message_sender = send_message(update, ctx)

    where_options = {
        "deadline": {
            "gte": datetime.now()
        },
    }

    if not for_admin:
        head = await db.user.find_unique(
            where={
                "tel_id": user_id
            }
        )

        where_options["team"] = head.team

    questions_boxes = await db.questionsbox.find_many(
        where=where_options
    )

    text = f"{title}\n\n"
    keyboard_buttons = []

    for qb in questions_boxes:
        deadline = datetime.now()

        text += (
            f"نام آزمون: {qb.label}\n"
            f"مدت زمان آزمون: {qb.duration}\n"
            f"ددلاین: {deadline}\n"
            f"تیم: {qb.team.replace('_', ' ')}\n"
            "-----------------------------------\n\n"
        )

        keyboard_buttons.append(
            [InlineKeyboardButton(
                f"{qb.label}", callback_data=f"{prefix} {qb.id}")]
        )

    keyboard_buttons.append(
        [InlineKeyboardButton(
            "بازگشت به لیست کارای ادمینی", callback_data=BACK_TO_ADMIN_ACTIONS)] if for_admin else [InlineKeyboardButton(
                "🎛️ " + "بازگشت به منوی کارای هدی", callback_data=BACK_TO_HEAD_ACTIONS)],
    )

    keyboard_buttons.append(
        [get_back_to_menu_button()]
    )

    await message_sender(text, reply_markup=InlineKeyboardMarkup(keyboard_buttons))

    return InlineKeyboardMarkup(keyboard_buttons)
