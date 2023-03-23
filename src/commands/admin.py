from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime
import json

from src.utils.db import db
from src.utils.is_there_admin import is_there_admin
from src.utils.is_admin import is_admin
from src.utils.ignore_command import ignore_command
from src.utils.show_user import show_user
from src.constants.commands import REGISTER_ADMIN
from src.constants.states import AdminStates
from src.constants.commands import ADMIN_SHOW_USERS_LIST, BACK_TO_ADMIN_ACTIONS, BACK_TO_MENU, ADMIN_PROMPT_ADD_QUESTION_BOX
from src.constants.other import LAST_MESSAGE_KEY


async def show_admin_actions(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    should_ignore = await ignore_command(update, ctx)

    if should_ignore:
        return ConversationHandler.END

    last_message = ctx.user_data.get(LAST_MESSAGE_KEY)

    keyboard_buttons = []

    if not await is_there_admin():
        keyboard_buttons.append(InlineKeyboardButton(
            "Register Admin", callback_data=REGISTER_ADMIN))

        sent_message = await ctx.bot.send_message(chat_id=update.effective_chat.id, text="There is no admin please register ASAP.", reply_markup=InlineKeyboardMarkup([keyboard_buttons]))
        ctx.user_data[LAST_MESSAGE_KEY] = sent_message.id

        return AdminStates.REGISTER_ADMIN

    keyboard_buttons.append(
        InlineKeyboardButton("Add question box",
                             callback_data=ADMIN_PROMPT_ADD_QUESTION_BOX)
    )

    keyboard_buttons.append(
        InlineKeyboardButton("Show list of users",
                             callback_data=ADMIN_SHOW_USERS_LIST)
    )

    keyboard = InlineKeyboardMarkup(
        [
            keyboard_buttons,
            [InlineKeyboardButton("Back", callback_data=BACK_TO_MENU)]
        ]
    )

    sent_message = None

    if last_message:
        sent_message = await ctx.bot.edit_message_text(message_id=last_message, chat_id=update.effective_chat.id, text="Here is the list of actions can do?", reply_markup=keyboard)
    else:
        sent_message = await ctx.bot.send_message(chat_id=update.effective_chat.id, text="Here is the list of actions can do?", reply_markup=keyboard)

    ctx.user_data[LAST_MESSAGE_KEY] = sent_message.id

    return AdminStates.ADMIN_ACTIONS


async def register_admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    should_ignore = await ignore_command(update, ctx)

    if should_ignore:
        return ConversationHandler.END

    user_id = update.effective_user.id
    last_message = ctx.user_data.get(LAST_MESSAGE_KEY)

    await db.user.update(
        where={
            "tel_id": user_id
        },
        data={
            "is_admin": True
        }
    )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Back To Actions", callback_data=BACK_TO_ADMIN_ACTIONS)
            ]
        ]
    )

    sent_message = await ctx.bot.edit_message_text(message_id=last_message, chat_id=update.effective_chat.id, text="Your account has been register as admin.", reply_markup=keyboard)
    ctx.user_data[LAST_MESSAGE_KEY] = sent_message.id

    return AdminStates.SHOW_ADMIN_ACTIONS


async def add_question_box(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    should_ignore = await ignore_command(update, ctx)

    if should_ignore:
        return ConversationHandler.END

    callback_query = update.callback_query
    last_message = ctx.user_data.get(LAST_MESSAGE_KEY)

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Back To Actions", callback_data=BACK_TO_ADMIN_ACTIONS)
            ]
        ]
    )

    if callback_query:
        sent_message = await ctx.bot.edit_message_text(message_id=last_message, chat_id=update.effective_chat.id, text="please send me json file of questions", reply_markup=keyboard)
        ctx.user_data[LAST_MESSAGE_KEY] = sent_message.id

        return AdminStates.ADMIN_ACTIONS

    file = await update.message.document.get_file()

    """
    json that is sent to bot should follow these structures:
        {
            "label": str,
            "duration": int,
            "deadline": iso time,
            "questions": [
              {
                "label": str,
                "score", int,
                "options": [
                    {
                        "label": str,
                        "is_answer": bool,
                    }
                ]
              }
            ]
        }

        at least one question with four answers minimum is required
    """
    parsed_file = json.loads(await file.download_as_bytearray())

    question_box = await db.questionsbox.create(
        data={
            "label": parsed_file["label"],
            "duration": int(parsed_file["duration"]),
            "deadline": datetime.fromisoformat(parsed_file["deadline"]),
        }
    )

    for question in parsed_file["questions"]:
        await db.question.create(
            data={
                "question": question["label"],
                "score": question["score"],
                "options": {
                    "create": list(map(lambda option: {
                        "label": option["label"],
                        "is_answer": option["is_answer"]
                    }, question["options"]))
                },
                "question_box": {
                    "connect": {
                        "id": question_box.id
                    }
                }
            }
        )

    sent_message = await ctx.bot.send_message(chat_id=update.effective_chat.id, text="Wow, you successfully added a question box", reply_markup=keyboard)
    ctx.user_data[LAST_MESSAGE_KEY] = sent_message.id

    return AdminStates.SHOW_ADMIN_ACTIONS


async def show_users_list(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    should_ignore = await ignore_command(update, ctx)

    if should_ignore:
        return ConversationHandler.END

    last_message = ctx.user_data.get(LAST_MESSAGE_KEY)

    users = await db.user.find_many(
        order={
            "is_admin": "desc"
        }
    )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Back To Actions", callback_data=BACK_TO_ADMIN_ACTIONS)
            ]
        ]
    )

    users_template = ""

    for i, user in enumerate(users):
        users_template += show_user(user.nickname, user.student_code,
                                    user.is_admin, i + 1)

    await ctx.bot.edit_message_text(message_id=last_message, chat_id=update.effective_chat.id, text=users_template, reply_markup=keyboard)

    return AdminStates.ADMIN_ACTIONS


async def cancel_admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data[LAST_MESSAGE_KEY] = None

    return ConversationHandler.END
