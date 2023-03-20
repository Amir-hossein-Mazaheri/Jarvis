from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

from src.constants.states import EditStates

# ASK_TO_EDIT_WHAT, EDIT_DECIDER, EDIT_NICKNAME, EDIT_STUDENT_CODE = range(4)

EDIT_ACTIONS = {
    "student_code": "Student Code",
    "nickname": "Nickname"
}


async def ask_to_edit_what(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [[EDIT_ACTIONS["student_code"], EDIT_ACTIONS["nickname"]]]

    keyboard = ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, input_field_placeholder="Pick one...")

    await update.message.reply_text(text="Please send me what you want to edit?", reply_markup=keyboard)

    return EditStates.EDIT_DECIDER


async def edit_decider(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    action = update.message.text

    if action == EDIT_ACTIONS["nickname"]:
        await update.message.reply_text(text="Please send me your new nickname", reply_markup=ReplyKeyboardRemove())

        return EditStates.EDIT_NICKNAME
    elif action == EDIT_ACTIONS["student_code"]:
        await update.message.reply_text(text="Please send me your new student code", reply_markup=ReplyKeyboardRemove())

        return EditStates.EDIT_STUDENT_CODE

    await update.message.reply_text(text="Invalid action.")

    return EditStates.ASK_TO_EDIT_WHAT


async def cancel_edit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text="Edit canceled.")

    return ConversationHandler.END
