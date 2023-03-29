from telegram import Update
from telegram.ext import ContextTypes
from prisma.enums import UserRole

from src.utils.db import db


async def is_head(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    user = await db.user.find_first(
        where={
            'tel_id': user_id,
            # this is "OR" because admin is also a head 
            "OR": [
                {
                    'role': UserRole.HEAD
                },
                {
                    'role': UserRole.ADMIN
                }
            ]
        }
    )

    return bool(user)
