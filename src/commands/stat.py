from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from src.utils.get_actions_keyboard import get_actions_keyboard
from src.utils.db import db
from src.utils.ignore_user import ignore_user
from src.utils.question_box_result_template import question_box_result_template
from src.utils.get_back_to_menu_button import get_back_to_menu_button
from src.utils.send_message import send_message
from src.constants.commands import BACK_TO_STAT
from src.constants.states import StatStates


async def get_user_stat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    should_ignore = await ignore_user(update, ctx)

    if should_ignore:
        return ConversationHandler.END

    user_id = update.effective_user.id
    message_sender = send_message(update, ctx)

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
        await message_sender(text="توی هیچ آزمونی مشارکت نداشتی تا حالا", reply_markup=await get_actions_keyboard(update, ctx))
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

    await message_sender(text=text, reply_markup=keyboard)

    return StatStates.SELECT_QUESTION_BOX


async def show_question_box_stat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    should_ignore = await ignore_user(update, ctx)

    if should_ignore:
        return ConversationHandler.END

    question_box_id = int(update.callback_query.data)
    user_id = update.effective_user.id
    message_sender = send_message(update, ctx)

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

    await message_sender(text=result, reply_markup=keyboard)

    return StatStates.DECIDER


async def stat_decider(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    should_ignore = await ignore_user(update, ctx)

    if should_ignore:
        return ConversationHandler.END

    back_to_stat = update.callback_query.data

    if back_to_stat:
        return await get_user_stat(update, ctx)

    return ConversationHandler.END
