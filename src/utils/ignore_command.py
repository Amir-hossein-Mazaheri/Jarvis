from telegram import Update
from telegram.ext import ContextTypes

from src.utils.is_admin import is_admin


async def ignore_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    admin = is_admin(user_id)

    if not admin:
        await ctx.bot.send_message(chat_id=update.effective_chat.id, text="You don't have access.")

    return admin
