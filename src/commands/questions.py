from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from prisma.models import QuestionOption
from datetime import datetime

from src.utils.db import db
from src.utils.get_next_question_id import get_next_question_id
from src.utils.show_questions_result import show_questions_result
from src.constants.states import QuestionStates
from src.constants.other import QUESTION_ID_KEY, NEXT_QUESTION_ID_KEY, CORRECT_QUESTIONS_KEY, WRONG_QUESTIONS_KEY


async def send_questions(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text="Here the list of this period questions...")

    question = await db.question.find_first(order={
        "created_at": "desc"
    }, include={
        "options": True
    }, where={
        "deadline": {
            "gte": datetime.now()
        }
    })

    keyboard = ReplyKeyboardMarkup(
        list(map(lambda option: [option.label], question.options)), one_time_keyboard=True, input_field_placeholder="Pick one...")

    text = (
        "<b>Answer The Question</b>\n\n"
        f"{question.question}"
    )

    await update.message.reply_text(text=text, reply_markup=keyboard)

    ctx.user_data[QUESTION_ID_KEY] = question.id

    return QuestionStates.ANSWER_VALIDATOR


async def answer_validator(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    answer = update.message.text
    user_id = update.effective_user.id
    question_id = ctx.user_data.get(QUESTION_ID_KEY)

    question = await db.question.find_unique(
        where={
            "id": question_id
        },
        include={
            "options": True
        }
    )

    correct_answer: QuestionOption = None

    for option in question.options:
        if option.is_answer:
            correct_answer = option
            break

    if correct_answer.label == answer:
        wrong_question_count = ctx.user_data.get(CORRECT_QUESTIONS_KEY)
        ctx.user_data[CORRECT_QUESTIONS_KEY] = wrong_question_count + \
            1 if wrong_question_count != None else 1

        await db.user.update(
            where={
                "tel_id": user_id
            },
            data={
                "correct_answered_questions": {
                    "connect": {
                        "id": question_id
                    }
                }
            }
        )
    else:
        wrong_question_count = ctx.user_data.get(CORRECT_QUESTIONS_KEY)
        ctx.user_data[WRONG_QUESTIONS_KEY] = wrong_question_count + \
            1 if wrong_question_count != None else 1

        await db.user.update(
            where={
                "tel_id": user_id
            },
            data={
                "wrong_answered_questions": {
                    "connect": {
                        "id": question_id
                    }
                }
            }
        )

    next_question_id = await get_next_question_id(question_id)

    if not bool(next_question_id):
        correct_answers = ctx.user_data.get(CORRECT_QUESTIONS_KEY)
        wrong_answers = ctx.user_data.get(WRONG_QUESTIONS_KEY)

        return await show_questions_result(update, correct_answers, wrong_answers)

    ctx.user_data[NEXT_QUESTION_ID_KEY] = next_question_id

    return QuestionStates.GET_NEXT_QUESTION


async def get_next_question(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    next_question_id = ctx.user_data.get(NEXT_QUESTION_ID_KEY)

    question = await db.question.find_unique(
        where={
            "id": next_question_id
        },
        include={
            "options": True
        }
    )

    keyboard = ReplyKeyboardMarkup(
        list(map(lambda option: [option.label], question.options)), one_time_keyboard=True, input_field_placeholder="Pick one...")

    text = (
        "<b>Answer The Question</b>\n\n"
        f"{question.question}"
    )

    await update.message.reply_text(text=text, reply_markup=keyboard)

    ctx.user_data[QUESTION_ID_KEY] = question.id

    return QuestionStates.ANSWER_VALIDATOR


async def skip_question(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    pass


async def quit_questions(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    pass


async def cancel_questions(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text="questions has been canceled")

    return ConversationHandler.END
