from telegram import Update
from telegram.ext import ContextTypes

from src.utils.is_admin import is_admin
from src.utils.get_actions_keyboard import get_actions_keyboard
from src.utils.send_message import send_message


async def ignore_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    admin = await is_admin(update, ctx)
    message_sender = send_message(update, ctx)

    if not admin:
        await message_sender(text="به این بخش دسترسی نداری داپش", reply_markup=await get_actions_keyboard(update, ctx))

    return not admin
