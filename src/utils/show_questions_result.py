from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, ContextTypes

from src.utils.db import db
from src.utils.question_box_result_template import question_box_result_template
from src.utils.get_actions_keyboard import get_actions_keyboard
from src.utils.send_message import send_message
from src.constants.other import CORRECT_QUESTIONS_KEY, WRONG_QUESTIONS_KEY, TOTAL_QUESTIONS_KEY, QUESTION_BOX_ID_KEY


async def show_questions_result(update: Update, ctx: ContextTypes.DEFAULT_TYPE, prefix: str = None):
    question_box_id = ctx.user_data.get(QUESTION_BOX_ID_KEY)
    user_id = update.effective_user.id
    message_sender = send_message(update, ctx)

    await db.user.update(
        where={
            "tel_id": user_id
        },
        data={
            "answered_questions_box": {
                "connect": {
                    "id": question_box_id
                }
            }
        }
    )

    correct_answers = ctx.user_data.get(CORRECT_QUESTIONS_KEY)
    wrong_answers = ctx.user_data.get(WRONG_QUESTIONS_KEY)
    total_answers = ctx.user_data.get(TOTAL_QUESTIONS_KEY)

    results = question_box_result_template(
        correct_answers, wrong_answers, total_answers, prefix)

    await message_sender(text=results, reply_markup=await get_actions_keyboard(update, ctx))

    # just make sure that old data doesn't conflict with new data in future
    ctx.user_data[CORRECT_QUESTIONS_KEY] = None
    ctx.user_data[WRONG_QUESTIONS_KEY] = None
    ctx.user_data[TOTAL_QUESTIONS_KEY] = None
    ctx.user_data[QUESTION_BOX_ID_KEY] = None

    return ConversationHandler.END
