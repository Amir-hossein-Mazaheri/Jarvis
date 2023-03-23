from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime
import json

from src.utils.db import db
from src.utils.get_next_question_id import get_next_question_id
from src.utils.show_questions_result import show_questions_result
from src.utils.show_question import show_question
from src.utils.ignore_user import ignore_user
from src.utils.get_actions_keyboard import get_actions_keyboard
from src.utils.get_back_to_menu_button import get_back_to_menu_button
from src.constants.states import QuestionStates
from src.constants.other import QUESTION_ID_KEY, NEXT_QUESTION_ID_KEY, CORRECT_QUESTIONS_KEY, WRONG_QUESTIONS_KEY, TOTAL_QUESTIONS_KEY, SEEN_QUESTIONS_KEY, QUESTION_BOX_ID_KEY, LAST_MESSAGE_KEY
from src.constants.commands import START_QUESTIONS


async def prep_phase(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    should_ignore = await ignore_user(update, ctx)

    if should_ignore:
        return ConversationHandler.END

    user_id = update.effective_user.id
    last_message = ctx.user_data.get(LAST_MESSAGE_KEY)

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🚀 " + "شروع", callback_data=START_QUESTIONS),
             get_back_to_menu_button("❌ " + "بازگشت")]
        ]
    )

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
        sent_message = await ctx.bot.edit_message_text(message_id=last_message, chat_id=update.effective_chat.id, text="فعلا آزمونی برای نمایش نداریم", reply_markup=await get_actions_keyboard(update, ctx))
        ctx.user_data[LAST_MESSAGE_KEY] = sent_message.id

        return ConversationHandler.END

    text = (
        f"آزمون {question_box.label}\n\n"
        f"مدت زمان آزمون {question_box.duration} دقیقه\n\n"
        "برای شروع آزمون <b>شروع</b> رو بزن"
    )

    sent_message = await ctx.bot.edit_message_text(message_id=last_message, chat_id=update.effective_chat.id, text=text, reply_markup=keyboard)
    ctx.user_data[LAST_MESSAGE_KEY] = sent_message.id

    ctx.user_data[QUESTION_BOX_ID_KEY] = question_box.id

    return QuestionStates.SHOW_QUESTIONS


async def send_questions(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    should_ignore = await ignore_user(update, ctx)

    if should_ignore:
        return ConversationHandler.END

    question_box_id = ctx.user_data.get(QUESTION_BOX_ID_KEY)

    question = await db.question.find_first(
        where={
            "question_box_id": question_box_id
        },
        order={
            "created_at": "desc"
        },
        include={
            "options": True
        }
    )

    questions_count = await db.question.count(where={"question_box_id": question_box_id})

    await show_question(update, ctx, question.question, question.options)

    ctx.user_data[QUESTION_ID_KEY] = question.id
    ctx.user_data[TOTAL_QUESTIONS_KEY] = questions_count
    ctx.user_data[SEEN_QUESTIONS_KEY] = json.dumps([question.id])

    return QuestionStates.ANSWER_VALIDATOR


async def answer_validator(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    should_ignore = await ignore_user(update, ctx)

    if should_ignore:
        return ConversationHandler.END

    answer_id = int(update.callback_query.data)

    user_id = update.effective_user.id
    question_id = ctx.user_data.get(QUESTION_ID_KEY)
    question_box_id = ctx.user_data.get(QUESTION_BOX_ID_KEY)

    answer = await db.questionoption.find_first(
        where={
            "id": answer_id,
            "question_id": question_id
        }
    )

    if not bool(answer):
        sent_message = await ctx.bot.send_message(update.effective_chat.id, "یکی از جوابایی که دیدی رو انتخاب کن")
        ctx.user_data[LAST_MESSAGE_KEY] = sent_message.id

        return QuestionStates.ANSWER_VALIDATOR

    if answer.is_answer:
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
    should_ignore = await ignore_user(update, ctx)

    if should_ignore:
        return ConversationHandler.END

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

    await show_question(update, ctx, question.question, question.options)

    ctx.user_data[QUESTION_ID_KEY] = question.id
    ctx.user_data[SEEN_QUESTIONS_KEY] = json.dumps(seen_questions)

    return QuestionStates.ANSWER_VALIDATOR


async def skip_question(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    should_ignore = await ignore_user(update, ctx)

    if should_ignore:
        return ConversationHandler.END

    question_id = ctx.user_data.get(QUESTION_ID_KEY)
    seen_questions = json.loads(ctx.user_data.get(SEEN_QUESTIONS_KEY))
    question_box_id = ctx.user_data.get(QUESTION_BOX_ID_KEY)
    next_question_id = await get_next_question_id(question_box_id, question_id, seen_questions)

    if not bool(next_question_id):
        return await show_questions_result(update, ctx)

    ctx.user_data[NEXT_QUESTION_ID_KEY] = next_question_id

    return await get_next_question(update, ctx)


async def quit_questions(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    should_ignore = await ignore_user(update, ctx)

    if should_ignore:
        return ConversationHandler.END

    should_ignore = await ignore_user(update, ctx)

    if should_ignore:
        return ConversationHandler.END

    return await show_questions_result(update, ctx)
