from telegram import Update
from telegram.ext import ContextTypes

from src.utils.is_user_registered import is_user_registered
from src.constants.other import LAST_MESSAGE_KEY
from src.utils.get_actions_keyboard import get_actions_keyboard


async def ignore_user(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_registered = await is_user_registered(user_id)

    if not is_registered:
        sent_message = await ctx.bot.send_message(chat_id=update.effective_chat.id, text="Please first register", reply_markup=await get_actions_keyboard(update, ctx))
        ctx.user_data[LAST_MESSAGE_KEY] = sent_message.id

    return not is_registered
