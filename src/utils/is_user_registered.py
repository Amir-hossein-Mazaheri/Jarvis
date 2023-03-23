from telegram import Update
from telegram.ext import ContextTypes

from src.utils.db import db
from src.constants.other import IS_USER_REGISTERED


async def is_user_registered(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_user_registered_cache = ctx.user_data.get(IS_USER_REGISTERED)

    if is_user_registered_cache:
        return bool(int(is_user_registered_cache))

    user = await db.user.find_unique(
        where={
            'tel_id': user_id
        }
    )

    ctx.user_data[IS_USER_REGISTERED] = int(bool(user))

    return bool(user)
