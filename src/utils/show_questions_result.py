from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, ContextTypes
from src.constants.other import CORRECT_QUESTIONS_KEY, WRONG_QUESTIONS_KEY, TOTAL_QUESTIONS_KEY


async def show_questions_result(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text="Nice you reached the end, good job.", reply_markup=ReplyKeyboardRemove())

    correct_answers = ctx.user_data.get(CORRECT_QUESTIONS_KEY)
    wrong_answers = ctx.user_data.get(WRONG_QUESTIONS_KEY)
    total_answers = ctx.user_data.get(TOTAL_QUESTIONS_KEY)

    results = (
        "📃 Here is the result of what you did today: \n\n"
        f"🟢 <b>Correct Answers</b>: {correct_answers if correct_answers != None else 0} \n"
        f"🔴 Wrong Answers: {wrong_answers if wrong_answers != None else 0} \n"
        f"⭕ Empty Answers: {total_answers} \n\n"
        "you did a great job 👏"
    )

    await update.message.reply_text(text=results)

    # just make sure that old data doesn't conflict with new data in future
    ctx.user_data[CORRECT_QUESTIONS_KEY] = None
    ctx.user_data[WRONG_QUESTIONS_KEY] = None
    ctx.user_data[TOTAL_QUESTIONS_KEY] = None

    return ConversationHandler.END
