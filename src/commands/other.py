from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from src.utils.db import db
from src.utils.ignore_user import ignore_user
from src.constants.states import StatStates
from src.constants.commands import NEXT_QUESTIONS_PAGE, PREV_QUESTIONS_PAGE
from src.constants.other import LAST_QUESTIONS_PAGE_KEY, QUESTIONS_PER_PAGE, LAST_MESSAGE_KEY
from src.utils.question_history_template import question_history_template
from src.utils.get_actions_keyboard import get_actions_keyboard


async def show_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    pass


async def questions_history(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    should_ignore = await ignore_user(update, ctx)

    if should_ignore:
        return ConversationHandler.END

    next_page = update.callback_query
    page = ctx.user_data.get(LAST_QUESTIONS_PAGE_KEY)

    curr_page = int(page) if next_page else 1

    if next_page:
        if next_page.data == NEXT_QUESTIONS_PAGE:
            curr_page += 1
        else:
            curr_page -= 1

    questions = await db.question.find_many(
        take=QUESTIONS_PER_PAGE,
        skip=(curr_page - 1) * QUESTIONS_PER_PAGE,
        include={
            "options": True
        }
    )

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
        [keyboard_buttons]
    )

    questions_template = ""

    for question in questions:
        questions_template += question_history_template(
            question.question, question.options)

    ctx.user_data[LAST_QUESTIONS_PAGE_KEY] = curr_page

    sent_message = None

    if next_page:
        last_message = ctx.user_data.get(LAST_MESSAGE_KEY)
        sent_message = await ctx.bot.edit_message_text(message_id=last_message, chat_id=update.effective_chat.id, text=questions_template, reply_markup=keyboard)
    else:
        sent_message = await ctx.bot.send_message(chat_id=update.effective_chat.id, text=questions_template, reply_markup=keyboard)

    ctx.user_data[LAST_MESSAGE_KEY] = sent_message.id
