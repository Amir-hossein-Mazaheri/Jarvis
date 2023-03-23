from telegram import Update
from telegram.ext import ContextTypes

from src.utils.is_admin import is_admin
from src.utils.get_actions_keyboard import get_actions_keyboard
from src.utils.send_message import send_message


async def ignore_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    admin = await is_admin(user_id)
    message_sender = send_message(update, ctx)

    if not admin:
        await message_sender(text="You don't have access.", reply_markup=await get_actions_keyboard(update, ctx), edit=False)

    return not admin
