from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from src.constants.other import STUDENT_CODE_LENGTH, RegisterMode
from src.commands.edit import EDIT_STUDENT_CODE

ASK_FOR_STUDENT_CODE, REGISTER_STUDENT_CODE, REGISTER_NICKNAME = range(3)


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text="Welcome to Staff Bot Manger")


async def ask_for_student_code(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text="This step in needed for registering your info, please send me your student number")

    return REGISTER_STUDENT_CODE


def register_student_code(mode: RegisterMode):
    """
        This function return a bot handler function because it has to act
        for two purpose, editing and creating student code but the reply text and action
        after that differ, for that issue I made the parent function to take an arg
    """

    async def register_student_code_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        username = update.effective_user.username.lower()
        student_code = update.message.text

        if len(student_code) != STUDENT_CODE_LENGTH:
            await update.message.reply_text(text="Invalid student id please send again")

            if mode == RegisterMode.CREATE:
                return REGISTER_STUDENT_CODE
            else:
                return EDIT_STUDENT_CODE

        # TODO: add logic for saving student number with username

        reply_text = ""

        if mode == RegisterMode.CREATE:
            reply_text = "now sends me your nick name on the bot"
        else:
            reply_text = "Cool, your student code has been changed."

        await update.message.reply_text(text=reply_text)

        if mode == RegisterMode.CREATE:
            return REGISTER_NICKNAME
        else:
            return ConversationHandler.END

    return register_student_code_action


def register_nickname(mode: RegisterMode):
    async def register_nickname_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        username = update.effective_user.username.lower()
        nickname = update.message.text

        # TODO: add logic to sign nickname to user

        reply_text = ""

        if mode == RegisterMode.CREATE:
            reply_text = "Thanks now, you're setup :)"
        else:
            reply_text = "Cool, your nickname been changed."

        await update.message.reply_text(text=reply_text)

        return ConversationHandler.END

    return register_nickname_action


async def cancel_registration(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text="registration canceled")

    return ConversationHandler.END
