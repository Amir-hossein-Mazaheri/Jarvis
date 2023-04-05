import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest

from src.constants.other import LAST_MESSAGE_KEY


def send_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """ 
    This is function to simplify process of sending message
    Most of this bot messages are edit of last message but this approach has some downsides
    If bot server get restarted and the user is in the middle of conversation last message will be discarded and the whole flow get ruined
    But with the help of this function, it will detect this and send a new message
    """
    chat_id = update.effective_chat.id
    last_message_id = ctx.user_data.get(LAST_MESSAGE_KEY)

    async def send_message(text: str, reply_markup=None, edit=True):
        sent_message = None

        try:
            if edit:
                if last_message_id:
                    sent_message = await ctx.bot.edit_message_text(message_id=last_message_id, chat_id=chat_id, text=text, reply_markup=reply_markup)
                else:
                    sent_message = await ctx.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
            else:
                sent_message = await ctx.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)

            ctx.user_data[LAST_MESSAGE_KEY] = sent_message.id
        except BadRequest as ex:
            logging.error(ex.message)

        return sent_message

    return send_message
