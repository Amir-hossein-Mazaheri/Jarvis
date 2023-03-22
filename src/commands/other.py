from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from src.utils.db import db
from src.utils.question_box_result_template import question_box_result_template
from src.constants.states import StatStates
from src.constants.commands import BACK_TO_STAT, NEXT_QUESTIONS_PAGE, PREV_QUESTIONS_PAGE
from src.constants.other import LAST_USER_STAT_MESSAGE_KEY, LAST_USER_QUESTION_BOX_STAT_KEY, LAST_QUESTIONS_PAGE_KEY, QUESTIONS_PER_PAGE, LAST_QUESTIONS_MESSAGE_KEY
from src.utils.question_history_template import question_history_template


async def show_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        InlineKeyboardButton("Show questions", switch_inline_query=True)
    ])


async def get_user_stat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    question_boxes = await db.questionsbox.find_many(
        where={
            "users": {
                "some": {
                    "tel_id": user_id
                }
            }
        }
    )

    text = "Here is the list of question boxes you participated in: \n\n"

    keyboard = InlineKeyboardMarkup(
        list(map(lambda qb: [InlineKeyboardButton(
            qb.label, callback_data=qb.id)], question_boxes))
    )

    sent_message = await ctx.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=keyboard)
    ctx.user_data[LAST_USER_STAT_MESSAGE_KEY] = sent_message.id

    return StatStates.SELECT_QUESTION_BOX


async def show_question_box_stat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    question_box_id = int(update.callback_query.data)
    last_user_stat = ctx.user_data.get(LAST_USER_STAT_MESSAGE_KEY)
    user_id = update.effective_user.id

    question_box = await db.user.find_unique(
        where={
            "tel_id": user_id
        },
        include={
            "correct_answered_questions": {
                "where": {
                    "question_box_id": question_box_id
                }
            },
            "wrong_answered_questions": {
                "where": {
                    "question_box_id": question_box_id
                }
            }
        }
    )

    questions_count = await db.question.count(where={"question_box_id": question_box_id})

    correct_answers = len(question_box.correct_answered_questions)
    wrong_answers = len(question_box.wrong_answered_questions)
    empty_answers = questions_count - correct_answers - wrong_answers

    result = question_box_result_template(
        correct_answers, wrong_answers, empty_answers)

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Back To List", callback_data=BACK_TO_STAT)]
        ]
    )

    sent_message = await ctx.bot.edit_message_text(message_id=last_user_stat, chat_id=update.effective_chat.id, text=result, reply_markup=keyboard)
    ctx.user_data[LAST_USER_QUESTION_BOX_STAT_KEY] = sent_message.id

    return StatStates.DECIDER


async def stat_decider(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    back_to_stat = update.callback_query.data
    last_user_question_box_stat = ctx.user_data.get(
        LAST_USER_QUESTION_BOX_STAT_KEY)

    await ctx.bot.delete_message(
        chat_id=update.effective_chat.id, message_id=last_user_question_box_stat)

    ctx.user_data[LAST_USER_STAT_MESSAGE_KEY] = None
    ctx.user_data[LAST_USER_QUESTION_BOX_STAT_KEY] = None

    if back_to_stat:
        return await get_user_stat(update, ctx)

    return ConversationHandler.END


async def questions_history(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
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
        last_question_message = ctx.user_data.get(LAST_QUESTIONS_MESSAGE_KEY)
        sent_message = await ctx.bot.edit_message_text(message_id=last_question_message, chat_id=update.effective_chat.id, text=questions_template, reply_markup=keyboard)
    else:
        sent_message = await ctx.bot.send_message(chat_id=update.effective_chat.id, text=questions_template, reply_markup=keyboard)

    ctx.user_data[LAST_QUESTIONS_MESSAGE_KEY] = sent_message.id


async def cancel_stat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await ctx.bot.send_message(chat_id=update.effective_chat.id, text="stat fetching canceled")

    return ConversationHandler.END
