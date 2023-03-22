from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from src.constants.states import EditStates
from src.utils.ignore_user import ignore_user
from src.constants.other import LAST_MESSAGE_KEY

EDIT_ACTIONS = {
    "student_code": "Student Code",
    "nickname": "Nickname"
}


async def ask_to_edit_what(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    should_ignore = await ignore_user(update, ctx)

    if should_ignore:
        return ConversationHandler.END

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(EDIT_ACTIONS["student_code"],
                              callback_data=EDIT_ACTIONS["student_code"])],
        [InlineKeyboardButton(EDIT_ACTIONS["nickname"],
                              callback_data=EDIT_ACTIONS["nickname"])]
    ])

    sent_message = await ctx.bot.send_message(chat_id=update.effective_chat.id, text="Please send me what you want to edit?", reply_markup=keyboard)
    ctx.user_data[LAST_MESSAGE_KEY] = sent_message.id

    return EditStates.EDIT_DECIDER


async def edit_decider(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    action = update.callback_query.data

    if action == EDIT_ACTIONS["nickname"]:
        sent_message = await ctx.bot.send_message(chat_id=update.effective_chat.id, text="Please send me your new nickname")
        ctx.user_data[LAST_MESSAGE_KEY] = sent_message.id

        return EditStates.EDIT_NICKNAME
    elif action == EDIT_ACTIONS["student_code"]:
        sent_message = await ctx.bot.send_message(chat_id=update.effective_chat.id, text="Please send me your new student code")
        ctx.user_data[LAST_MESSAGE_KEY] = sent_message.id

        return EditStates.EDIT_STUDENT_CODE

    sent_message = await ctx.bot.send_message(chat_id=update.effective_chat.id, text="Invalid action.")
    ctx.user_data[LAST_MESSAGE_KEY] = sent_message.id

    return EditStates.ASK_TO_EDIT_WHAT


async def cancel_edit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    sent_message = await ctx.bot.send_message(chat_id=update.effective_chat.id, text="Edit canceled.")
    ctx.user_data[LAST_MESSAGE_KEY] = sent_message.id

    return ConversationHandler.END
