from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

from src.utils.db import db
from src.utils.get_back_to_menu_button import get_back_to_menu_button
from src.constants.commands import BACK_TO_TASKS_ACTIONS


async def get_tasks_keyboard(user_id: int, prefix: str, without_marked: bool):
    where_options = {
        'approved': False,

        'deadline': {
            'gte': datetime.now()
        },

        'user': {
            "tel_id": user_id
        }
    }

    where_options["markDone"] = not without_marked

    tasks = await db.task.find_many(
        where=where_options
    )

    keyboard_buttons = []
    is_there_any_tasks = len(tasks) != 0

    for task in tasks:
        keyboard_buttons.append(
            [InlineKeyboardButton(task.job, callback_data=f"{prefix} {task.id}")])

    keyboard_buttons.append(
        [InlineKeyboardButton(
            "⏮️ " + "بازگشت به منوی تسک ها", callback_data=BACK_TO_TASKS_ACTIONS)],
    )
    keyboard_buttons.append([get_back_to_menu_button()])

    return (InlineKeyboardMarkup(keyboard_buttons), is_there_any_tasks)
