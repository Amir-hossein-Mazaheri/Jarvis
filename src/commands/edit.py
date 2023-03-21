from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from src.constants.states import EditStates

EDIT_ACTIONS = {
    "student_code": "Student Code",
    "nickname": "Nickname"
}


async def ask_to_edit_what(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    # reply_keyboard = [[EDIT_ACTIONS["student_code"], EDIT_ACTIONS["nickname"]]]

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(EDIT_ACTIONS["student_code"],
                              callback_data=EDIT_ACTIONS["student_code"])],
        [InlineKeyboardButton(EDIT_ACTIONS["nickname"],
                              callback_data=EDIT_ACTIONS["nickname"])]
    ])

    await update.message.reply_text(text="Please send me what you want to edit?", reply_markup=keyboard)

    return EditStates.EDIT_DECIDER


async def edit_decider(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    action = update.callback_query.data

    if action == EDIT_ACTIONS["nickname"]:
        await ctx.bot.send_message(chat_id=update.effective_chat.id, text="Please send me your new nickname")

        return EditStates.EDIT_NICKNAME
    elif action == EDIT_ACTIONS["student_code"]:
        await ctx.bot.send_message(chat_id=update.effective_chat.id, text="Please send me your new student code")

        return EditStates.EDIT_STUDENT_CODE

    await ctx.bot.send_message(chat_id=update.effective_chat.id, text="Invalid action.")

    return EditStates.ASK_TO_EDIT_WHAT


async def cancel_edit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text="Edit canceled.")

    return ConversationHandler.END
