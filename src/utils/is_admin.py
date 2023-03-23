from telegram import Update
from telegram.ext import ContextTypes

from src.utils.db import db


async def is_admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    user = await db.user.find_first(
        where={
            'tel_id': user_id,
            'is_admin': True
        }
    )

    return bool(user)
