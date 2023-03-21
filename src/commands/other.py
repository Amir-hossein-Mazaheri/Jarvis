from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from src.utils.db import db
from src.utils.question_box_result_template import question_box_result_template
from src.constants.states import StatStates
from src.constants.commands import BACK_TO_STAT
from src.constants.other import LAST_USER_STAT_MESSAGE_KEY, LAST_USER_QUESTION_BOX_STAT_KEY


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

    # await ctx.bot.delete_message(chat_id=update.effective_chat.id, message_id=last_user_stat)

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


async def cancel_stat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await ctx.bot.send_message(chat_id=update.effective_chat.id, text="stat fetching canceled")

    return ConversationHandler.END
