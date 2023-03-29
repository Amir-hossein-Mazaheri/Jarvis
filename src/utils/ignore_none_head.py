from telegram import Update
from telegram.ext import ContextTypes

from src.utils.is_head import is_head
from src.utils.send_message import send_message
from src.utils.get_actions_keyboard import get_actions_keyboard


async def ignore_none_head(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    is_user_head = await is_head(update, ctx)
    message_sender = send_message(update, ctx)

    if not is_user_head:
        await message_sender(text="متاسفانه به این بخش دسترسی ندارید", reply_markup=await get_actions_keyboard(update, ctx))

    return not is_user_head
