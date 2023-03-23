from telegram import Update
from telegram.ext import ContextTypes

from src.utils.is_user_registered import is_user_registered
from src.utils.send_message import send_message
from src.utils.get_actions_keyboard import get_actions_keyboard


async def ignore_user(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    is_registered = await is_user_registered(update, ctx)
    message_sender = send_message(update, ctx)

    if not is_registered:
        await message_sender(text="Please first register", reply_markup=await get_actions_keyboard(update, ctx), edit=False)

    return not is_registered
