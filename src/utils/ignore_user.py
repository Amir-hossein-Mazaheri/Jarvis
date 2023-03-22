from telegram import Update
from telegram.ext import ContextTypes

from src.utils.is_user_registered import is_user_registered


async def ignore_user(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_registered = await is_user_registered(user_id)

    if not is_registered:
        await ctx.bot.send_message(chat_id=update.effective_chat.id, text="Please first register via /register command")

    return not is_registered
