from telegram import Update
from telegram.ext import ContextTypes

from src.utils.db import db
from src.constants.other import IS_ADMIN_KEY


async def is_admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_admin_cache = ctx.user_data.get(IS_ADMIN_KEY)

    if is_admin_cache:
        return bool(int(is_admin_cache))

    user = await db.user.find_first(
        where={
            'tel_id': user_id,
            'is_admin': True
        }
    )

    ctx.user_data[IS_ADMIN_KEY] = str(int(bool(user)))

    return bool(user)
