from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from src.utils.get_actions_keyboard import get_actions_keyboard
from src.utils.db import db
from src.utils.ignore_user import ignore_user
from src.utils.question_box_result_template import question_box_result_template
from src.utils.get_back_to_menu_button import get_back_to_menu_button
from src.constants.commands import BACK_TO_STAT
from src.constants.states import StatStates
from src.constants.other import LAST_MESSAGE_KEY


async def get_user_stat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    should_ignore = await ignore_user(update, ctx)
    last_message = ctx.user_data.get(LAST_MESSAGE_KEY)

    if should_ignore:
        return ConversationHandler.END

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

    if len(question_boxes) == 0:
        sent_message = await ctx.bot.edit_message_text(message_id=last_message, chat_id=update.effective_chat.id, text="توی هیچ آزمونی مشارکت نداشتی تا حالا", reply_markup=await get_actions_keyboard(update, ctx))

        return ConversationHandler.END

    text = "📃 " + "لیست آزمون هایی که توش مشارکت داشتی: \n\n"

    keyboard_buttons = [
        [get_back_to_menu_button()]
    ]

    keyboard_buttons.extend(list(map(lambda qb: [InlineKeyboardButton(
        qb.label, callback_data=qb.id)], question_boxes)))

    keyboard = InlineKeyboardMarkup(
        keyboard_buttons
    )

    sent_message = await ctx.bot.edit_message_text(message_id=last_message, chat_id=update.effective_chat.id, text=text, reply_markup=keyboard)
    ctx.user_data[LAST_MESSAGE_KEY] = sent_message.id

    return StatStates.SELECT_QUESTION_BOX


async def show_question_box_stat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    should_ignore = await ignore_user(update, ctx)

    if should_ignore:
        return ConversationHandler.END

    question_box_id = int(update.callback_query.data)
    last_message = ctx.user_data.get(LAST_MESSAGE_KEY)
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
            [InlineKeyboardButton("بازگشت به لیست آزمون ها",
                                  callback_data=BACK_TO_STAT)],
            [get_back_to_menu_button()]
        ]
    )

    sent_message = await ctx.bot.edit_message_text(message_id=last_message, chat_id=update.effective_chat.id, text=result, reply_markup=keyboard)
    ctx.user_data[LAST_MESSAGE_KEY] = sent_message.id

    return StatStates.DECIDER


async def stat_decider(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    should_ignore = await ignore_user(update, ctx)

    if should_ignore:
        return ConversationHandler.END

    back_to_stat = update.callback_query.data

    if back_to_stat:
        return await get_user_stat(update, ctx)

    return ConversationHandler.END
