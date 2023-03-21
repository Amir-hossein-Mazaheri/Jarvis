from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from prisma.models import QuestionOption
from datetime import datetime
import json

from src.utils.db import db
from src.utils.get_next_question_id import get_next_question_id
from src.utils.show_questions_result import show_questions_result
from src.utils.show_question import show_question
from src.constants.states import QuestionStates
from src.constants.other import QUESTION_ID_KEY, NEXT_QUESTION_ID_KEY, CORRECT_QUESTIONS_KEY, WRONG_QUESTIONS_KEY, TOTAL_QUESTIONS_KEY, SEEN_QUESTIONS_KEY, QUESTION_BOX_ID_KEY


async def send_questions(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    question_box = await db.questionsbox.find_first(
        where={
            "deadline": {
                "gte": datetime.now()
            },
            "users": {
                "none": {
                    "tel_id": user_id
                }
            }
        })

    if not bool(question_box):
        await update.message.reply_text(text="Sorry there is no question to show you, you answered all of them either there is no question")
        return ConversationHandler.END

    question = await db.question.find_first(
        where={
            "question_box_id": question_box.id
        },
        order={
            "created_at": "desc"
        },
        include={
            "options": True
        }
    )

    await update.message.reply_text(text="Here the list of this period questions...")

    questions_count = await db.question.count(where={"question_box_id": question_box.id})

    await show_question(update, question.question, list(map(lambda option: option.label, question.options)))

    ctx.user_data[QUESTION_BOX_ID_KEY] = question_box.id
    ctx.user_data[QUESTION_ID_KEY] = question.id
    ctx.user_data[TOTAL_QUESTIONS_KEY] = questions_count
    ctx.user_data[SEEN_QUESTIONS_KEY] = json.dumps([question.id])

    return QuestionStates.ANSWER_VALIDATOR


async def answer_validator(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    answer = update.message.text
    user_id = update.effective_user.id
    question_id = ctx.user_data.get(QUESTION_ID_KEY)
    question_box_id = ctx.user_data.get(QUESTION_BOX_ID_KEY)

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

    # Decrement from total questions count
    # its useful for showing unanswered questions count
    total_questions_count = ctx.user_data.get(TOTAL_QUESTIONS_KEY)
    ctx.user_data[TOTAL_QUESTIONS_KEY] = total_questions_count - 1

    seen_questions = json.loads(ctx.user_data.get(SEEN_QUESTIONS_KEY))
    next_question_id = await get_next_question_id(question_box_id, question_id, seen_questions)

    if not bool(next_question_id):
        return await show_questions_result(update, ctx)

    ctx.user_data[NEXT_QUESTION_ID_KEY] = next_question_id

    return await get_next_question(update, ctx)


async def get_next_question(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    next_question_id = ctx.user_data.get(NEXT_QUESTION_ID_KEY)

    # these two lines makes sure that next question is added to seen questions list
    seen_questions: list[int] = json.loads(
        ctx.user_data.get(SEEN_QUESTIONS_KEY))
    seen_questions.append(next_question_id)

    question = await db.question.find_unique(
        where={
            "id": next_question_id
        },
        include={
            "options": True
        }
    )

    await show_question(update, question.question, list(map(lambda option: option.label, question.options)))

    ctx.user_data[QUESTION_ID_KEY] = question.id
    ctx.user_data[SEEN_QUESTIONS_KEY] = json.dumps(seen_questions)

    return QuestionStates.ANSWER_VALIDATOR


async def skip_question(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    question_id = ctx.user_data.get(QUESTION_ID_KEY)
    next_question_id = await get_next_question_id(question_id)

    if not bool(next_question_id):
        return await show_questions_result(update, ctx)

    ctx.user_data[NEXT_QUESTION_ID_KEY] = next_question_id

    return await get_next_question(update, ctx)


async def quit_questions(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    return show_questions_result(update, ctx)


async def cancel_questions(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text="questions has been canceled")

    return ConversationHandler.END
