from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from prisma.enums import UserRole

from src.utils.db import db
from src.utils.show_user import show_user
from src.utils.get_back_to_menu_button import get_back_to_menu_button
from src.constants.commands import BACK_TO_ADMIN_ACTIONS


async def get_users_keyboard(exclude_heads=False, data_prefix: str = None):
    keyboard = []

    users = await db.user.find_many(
        where={
            "NOT": {
                "OR": [
                    {
                        "role": UserRole.ADMIN
                    },
                    {"role": UserRole.HEAD} if exclude_heads else {}
                ]
            },
        }
    )

    for i, user in enumerate(users):
        callback_data = f"{data_prefix}~~~" if data_prefix else ""

        callback_data += str(user.id)

        keyboard.append([InlineKeyboardButton(show_user(
            user.nickname, user.student_code, user.role, i, ignore_trailing_dashes=True), callback_data=callback_data)])

    keyboard.append(
        [
            InlineKeyboardButton(
                "بازگشت به لیست کارای ادمینی", callback_data=BACK_TO_ADMIN_ACTIONS),
            get_back_to_menu_button()
        ]
    )

    return InlineKeyboardMarkup(keyboard)
