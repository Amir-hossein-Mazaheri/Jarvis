from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from src.utils.db import db
from src.utils.is_user_registered import is_user_registered
from src.constants.other import STUDENT_CODE_LENGTH, RegisterMode
from src.constants.states import RegisterStates, EditStates

# ASK_FOR_STUDENT_CODE, REGISTER_STUDENT_CODE, REGISTER_NICKNAME = range(3)


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text="Welcome to Staff Bot Manger")


async def ask_for_student_code(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if await is_user_registered(user_id):
        await update.message.reply_text(text="You already registered, if you want to edit your info use /edit command.")

        return ConversationHandler.END

    await update.message.reply_text(text="This step in needed for registering your info, please send me your student number")

    return RegisterStates.REGISTER_STUDENT_CODE


def register_student_code(mode: RegisterMode):
    """
        This function return a bot handler function because it has to act
        for two purpose, editing and creating student code but the reply text and action
        after that differ, for that issue I made the parent function to take an arg
    """

    async def register_student_code_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        name = update.effective_user.name
        student_code = update.message.text

        if len(student_code) != STUDENT_CODE_LENGTH:
            await update.message.reply_text(text="Invalid student id please send again")

            if mode == RegisterMode.CREATE:
                return RegisterStates.REGISTER_STUDENT_CODE
            else:
                return EditStates.EDIT_STUDENT_CODE

        await db.user.upsert(
            where={
                "tel_id": user_id,
            },
            data={
                "create": {
                    "tel_id": user_id,
                    "student_code": student_code,
                    "name": name,
                    "nickname": name,
                },
                "update": {
                    "student_code": student_code
                }
            }
        )

        reply_text = ""

        if mode == RegisterMode.CREATE:
            reply_text = "now sends me your nick name on the bot"
        else:
            reply_text = "Cool, your student code has been changed."

        await update.message.reply_text(text=reply_text)

        if mode == RegisterMode.CREATE:
            return RegisterStates.REGISTER_NICKNAME
        else:
            return ConversationHandler.END

    return register_student_code_action


def register_nickname(mode: RegisterMode):
    async def register_nickname_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        nickname = update.message.text

        await db.user.update(
            where={
                "tel_id": user_id
            },
            data={
                "nickname": nickname
            }
        )

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
