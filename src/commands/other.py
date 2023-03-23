from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime

from src.utils.db import db
from src.utils.ignore_user import ignore_user
from src.constants.commands import NEXT_QUESTIONS_PAGE, PREV_QUESTIONS_PAGE, BACK_TO_MENU
from src.constants.other import LAST_QUESTIONS_PAGE_KEY, QUESTIONS_PER_PAGE, LAST_MESSAGE_KEY
from src.utils.question_history_template import question_history_template
from src.utils.get_actions_keyboard import get_actions_keyboard


async def show_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    pass


async def questions_history(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    should_ignore = await ignore_user(update, ctx)
    last_message = ctx.user_data.get(LAST_MESSAGE_KEY)

    if should_ignore:
        return ConversationHandler.END

    callback_query = update.callback_query
    page = ctx.user_data.get(LAST_QUESTIONS_PAGE_KEY)

    curr_page = int(page) if page else 1

    if callback_query:
        data = callback_query.data

        if data == NEXT_QUESTIONS_PAGE:
            curr_page += 1
        elif data == PREV_QUESTIONS_PAGE:
            curr_page -= 1

    questions = await db.question.find_many(
        where={
            "question_box": {
                "deadline": {
                    "lte": datetime.now()
                }
            }
        },
        take=QUESTIONS_PER_PAGE,
        skip=(curr_page - 1) * QUESTIONS_PER_PAGE,
        include={
            "options": True
        }
    )

    if len(questions) == 0:
        return await ctx.bot.edit_message_text(message_id=last_message, chat_id=update.effective_chat.id, text="There is no questions yet", reply_markup=await get_actions_keyboard(update, ctx))

    questions_count = await db.question.count()

    total_pages = questions_count // QUESTIONS_PER_PAGE

    keyboard_buttons = []

    if curr_page < total_pages:
        keyboard_buttons.append(
            InlineKeyboardButton(
                "Next Page", callback_data=NEXT_QUESTIONS_PAGE)
        )

    if curr_page != 1:
        keyboard_buttons.append(
            InlineKeyboardButton(
                "Prev Page", callback_data=PREV_QUESTIONS_PAGE),
        )

    keyboard = InlineKeyboardMarkup(
        [keyboard_buttons, [InlineKeyboardButton(
            "Back To Menu", callback_data=BACK_TO_MENU)]]
    )

    questions_template = ""

    for question in questions:
        questions_template += question_history_template(
            question.question, question.options)

    ctx.user_data[LAST_QUESTIONS_PAGE_KEY] = curr_page

    sent_message = None

    if callback_query:
        sent_message = await ctx.bot.edit_message_text(message_id=last_message, chat_id=update.effective_chat.id, text=questions_template, reply_markup=keyboard)
    else:
        sent_message = await ctx.bot.send_message(chat_id=update.effective_chat.id, text=questions_template, reply_markup=keyboard)

    ctx.user_data[LAST_MESSAGE_KEY] = sent_message.id


async def back_to_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    last_message = ctx.user_data.get(LAST_MESSAGE_KEY)

    sent_message = await ctx.bot.edit_message_text(message_id=last_message, chat_id=update.effective_chat.id, text="Bot Menu", reply_markup=await get_actions_keyboard(update, ctx))
    ctx.user_data[LAST_MESSAGE_KEY] = sent_message.id

    # to make sure that it exits conversation wether it get used in conversation handler
    return ConversationHandler.END
